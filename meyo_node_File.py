import os
import csv
import openpyxl
import pathlib
import folder_paths
import torch
import node_helpers
import numpy as np
from PIL import Image, ImageOps, ImageSequence


#======加载重置图像
class LoadAndAdjustImage:
    _color_channels = ["alpha", "red", "green", "blue"]
    
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f.name for f in pathlib.Path(input_dir).iterdir() if f.is_file()]
        return {
            "required": {
                "image": (sorted(files), {"image_upload": True}),
                "max_dimension": ("INT", {"default": 1024, "min": 0, "max": 4096, "step": 8}),
                "size_option": (["Custom", "Small", "Medium", "Large"], {"default": "Custom"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("image", "mask", "width", "height")
    FUNCTION = "load_image"
    CATEGORY = "Meeeyo/File"

    def load_image(self, image, max_dimension, size_option):
        image_path = folder_paths.get_annotated_filepath(image)
        img = node_helpers.pillow(Image.open, image_path)

        W, H = img.size
        output_images = []
        output_masks = []

        for frame in ImageSequence.Iterator(img):
            frame = node_helpers.pillow(ImageOps.exif_transpose, frame)

            if frame.mode == 'P':
                frame = frame.convert("RGBA")
            elif 'A' in frame.getbands():
                frame = frame.convert("RGBA")

            if size_option != "Custom":
                aspect_ratio = W / H

                if size_option == "Small":
                    if aspect_ratio >= 1.23:
                        target_width, target_height = 768, 512
                    elif 0.82 < aspect_ratio < 1.23:
                        target_width, target_height = 768, 768
                    else:
                        target_width, target_height = 512, 768
                elif size_option == "Medium":
                    if aspect_ratio >= 1.23:
                        target_width, target_height = 1216, 832
                    elif 0.82 < aspect_ratio < 1.23:
                        target_width, target_height = 1216, 1216
                    else:
                        target_width, target_height = 832, 1216
                elif size_option == "Large":
                    if aspect_ratio >= 1.23:
                        target_width, target_height = 1600, 1120
                    elif 0.82 < aspect_ratio < 1.23:
                        target_width, target_height = 1600, 1600
                    else:
                        target_width, target_height = 1120, 1600

                image = frame.convert("RGB")
                image = ImageOps.fit(image, (target_width, target_height), method=Image.Resampling.BILINEAR, centering=(0.5, 0.5))

                if 'A' in frame.getbands():
                    mask = np.array(frame.getchannel('A')).astype(np.float32) / 255.0
                    mask = torch.from_numpy(mask)
                    mask_image = Image.fromarray((mask.numpy() * 255).astype(np.uint8))
                    mask_image = ImageOps.fit(mask_image, (target_width, target_height), method=Image.Resampling.BILINEAR, centering=(0.5, 0.5))
                    mask = np.array(mask_image).astype(np.float32) / 255.0
                    mask = torch.from_numpy(mask)
                else:
                    mask = torch.ones((target_height, target_width), dtype=torch.float32, device="cpu")
            else:
                ratio = min(max_dimension / W, max_dimension / H)
                adjusted_width = round(W * ratio)
                adjusted_height = round(H * ratio)

                image = frame.convert("RGB")
                image = image.resize((adjusted_width, adjusted_height), Image.Resampling.BILINEAR)

                if 'A' in frame.getbands():
                    mask = np.array(frame.getchannel('A')).astype(np.float32) / 255.0
                    mask = torch.from_numpy(mask)
                    mask_image = Image.fromarray((mask.numpy() * 255).astype(np.uint8))
                    mask_image = mask_image.resize((adjusted_width, adjusted_height), Image.Resampling.BILINEAR)
                    mask = np.array(mask_image).astype(np.float32) / 255.0
                    mask = torch.from_numpy(mask)
                else:
                    mask = torch.ones((adjusted_height, adjusted_width), dtype=torch.float32, device="cpu")

            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]
        if size_option != "Custom":
            return (output_image, output_mask, target_width, target_height)
        else:
            return (output_image, output_mask, adjusted_width, adjusted_height)

    @classmethod
    def VALIDATE_INPUTS(s, image):
        if not folder_paths.exists_annotated_filepath(image):
            return f"Invalid image file: {image}"
        return True


#======重置图像尺寸
class ImageAdjuster:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "max_dimension": ("INT", {"default": 1024, "min": 0, "max": 4096, "step": 8}),
                "size_option": (["Custom", "Small", "Medium", "Large"], {"default": "Custom"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "width", "height")
    FUNCTION = "process_image"
    CATEGORY = "Meeeyo/File"

    def process_image(self, image, max_dimension=1024, size_option="Custom"):
        input_image = Image.fromarray((image.squeeze(0).numpy() * 255).astype(np.uint8))
        W, H = input_image.size

        processed_images = []

        for frame in [input_image]:
            frame = ImageOps.exif_transpose(frame)

            if frame.mode == 'P':
                frame = frame.convert("RGBA")
            elif 'A' in frame.getbands():
                frame = frame.convert("RGBA")

            if size_option != "Custom":
                aspect_ratio = W / H

                if size_option == "Small":
                    if aspect_ratio >= 1.23:
                        target_width, target_height = 768, 512
                    elif 0.82 < aspect_ratio < 1.23:
                        target_width, target_height = 768, 768
                    else:
                        target_width, target_height = 512, 768
                elif size_option == "Medium":
                    if aspect_ratio >= 1.23:
                        target_width, target_height = 1216, 832
                    elif 0.82 < aspect_ratio < 1.23:
                        target_width, target_height = 1216, 1216
                    else:
                        target_width, target_height = 832, 1216
                elif size_option == "Large":
                    if aspect_ratio >= 1.23:
                        target_width, target_height = 1600, 1120
                    elif 0.82 < aspect_ratio < 1.23:
                        target_width, target_height = 1600, 1600
                    else:
                        target_width, target_height = 1120, 1600
                processed_image = frame.convert("RGB")
                processed_image = ImageOps.fit(processed_image, (target_width, target_height), method=Image.Resampling.BILINEAR, centering=(0.5, 0.5))
            else:
                ratio = min(max_dimension / W, max_dimension / H)
                adjusted_width = round(W * ratio)
                adjusted_height = round(H * ratio)

                processed_image = frame.convert("RGB")
                processed_image = processed_image.resize((adjusted_width, adjusted_height), Image.Resampling.BILINEAR)

            processed_image = np.array(processed_image).astype(np.float32) / 255.0
            processed_image = torch.from_numpy(processed_image)[None,]
            processed_images.append(processed_image)

        output_image = torch.cat(processed_images, dim=0) if len(processed_images) > 1 else processed_images[0]
        if size_option != "Custom":
            return (output_image, target_width, target_height)
        else:
            return (output_image, adjusted_width, adjusted_height)

#======保存图像
class SaveImagEX:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "save_path": ("STRING", {"default": "./output"}),
                "image_name": ("STRING", {"default": "ComfyUI"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "save_image"
    OUTPUT_NODE = True
    CATEGORY = "Meeeyo/File"

    def save_image(self, image, save_path, image_name):
        if not isinstance(image, torch.Tensor):
            raise ValueError("Invalid image tensor format")
        if save_path == "./output":
            save_path = self.output_dir
        elif not os.path.isabs(save_path):
            save_path = os.path.join(self.output_dir, save_path)
        os.makedirs(save_path, exist_ok=True)
        base_name = os.path.splitext(image_name)[0]
        batch_size = image.shape[0]
        channel_to_mode = {1: "L", 3: "RGB", 4: "RGBA"}

        for i in range(batch_size):
            filename = f"{base_name}.png" if batch_size == 1 else f"{base_name}_{i:05d}.png"
            full_path = os.path.join(save_path, filename)
            single_image = image[i].cpu().numpy()
            single_image = (single_image * 255).astype('uint8')
            channels = single_image.shape[2]
            if channels not in channel_to_mode:
                raise ValueError(f"Unsupported channel number: {channels}")
            mode = channel_to_mode[channels]
            if channels == 1:
                single_image = single_image[:, :, 0]
            pil_image = Image.fromarray(single_image, mode)
            pil_image.save(full_path, format="PNG", compress_level=0)
        return (image,)


#======文件路径和后缀统计
class FileListAndSuffix:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder_path": ("STRING",),
                "file_extension": (["jpg", "png", "jpg&png", "txt", "csv", "all"], {"default": "jpg"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING", "INT", "LIST")
    FUNCTION = "file_list_and_suffix"
    CATEGORY = "Meeeyo/File"

    def IS_CHANGED():
        return float("NaN")

    def file_list_and_suffix(self, folder_path, file_extension):
        try:
            if not os.path.isdir(folder_path):
                return ("", 0, [])

            if file_extension == "all":
                file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            elif file_extension == "jpg&png":
                file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png'))]
            else:
                file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.' + file_extension)]

            return ('\n'.join(file_paths), len(file_paths), file_paths)
        except Exception as e:
            return ("", 0, [])


#======读取表格数据
class ReadExcelData:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "excel_path": ("STRING", {"default": "path/to/your/file.xlsx"}),
                "sheet_name": ("STRING", {"default": "Sheet1"}),
                "row_range": ("STRING", {"default": "2-3"}),
                "col_range": ("STRING", {"default": "1-4"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "read_excel_data"
    CATEGORY = "Meeeyo/File"

    def IS_CHANGED():
        return float("NaN")

    def read_excel_data(self, excel_path, sheet_name, row_range, col_range):
        try:
            if "-" in row_range:
                start_row, end_row = map(int, row_range.split("-"))
            else:
                start_row = end_row = int(row_range)

            if "-" in col_range:
                start_col, end_col = map(int, col_range.split("-"))
            else:
                start_col = end_col = int(col_range)

            start_row = max(1, start_row)
            start_col = max(1, start_col)

            workbook = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
            sheet = workbook[sheet_name]

            output_lines = []
            for row in range(start_row, end_row + 1):
                row_data = []
                for col in range(start_col, end_col + 1):
                    cell_value = sheet.cell(row=row, column=col).value
                    row_data.append(str(cell_value) if cell_value is not None else "")
                output_lines.append("|".join(row_data))

            workbook.close()
            del workbook

            return ("\n".join(output_lines),)

        except Exception as e:
            return (f"Error: {str(e)}",)


#======写入表格数据
class WriteExcelData:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "excel_path": ("STRING", {"default": "path/to/your/file.xlsx"}),
                "sheet_name": ("STRING", {"default": "Sheet1"}), 
                "row_range": ("STRING", {"default": "2-3"}),
                "col_range": ("STRING", {"default": "1-4"}),
                "data": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "write_excel_data"
    CATEGORY = "Meeeyo/File"

    def IS_CHANGED():
        return float("NaN")

    def write_excel_data(self, excel_path, sheet_name, row_range, col_range, data):
        try:
            if not os.path.exists(excel_path):
                return (f"Error: File does not exist at path: {excel_path}",)

            if not os.access(excel_path, os.W_OK):
                return (f"Error: No write permission for file at path: {excel_path}",)

            if "-" in row_range:
                start_row, end_row = map(int, row_range.split("-"))
            else:
                start_row = end_row = int(row_range)

            if "-" in col_range:
                start_col, end_col = map(int, col_range.split("-"))
            else:
                start_col = end_col = int(col_range)

            start_row = max(1, start_row)
            start_col = max(1, start_col)

            workbook = openpyxl.load_workbook(excel_path, read_only=False, data_only=True)
            sheet = workbook[sheet_name]

            data_lines = data.strip().split("\n")

            for row_index, line in enumerate(data_lines, start=start_row):
                if row_index > end_row:
                    break

                cell_values = line.split("|")
                for col_index, cell_value in enumerate(cell_values, start=start_col):
                    if col_index > end_col:
                        break

                    if cell_value.strip():
                        sheet.cell(row=row_index, column=col_index).value = cell_value.strip()

            workbook.save(excel_path)

            workbook.close()
            del workbook

            return ("Data written successfully!",)

        except PermissionError as pe:
            return (f"Permission Error: {str(pe)}",)
        except Exception as e:
            return (f"Error: {str(e)}",)


#======查找表格数据
class FindExcelData:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "excel_path": ("STRING", {"default": "path/to/your/file.xlsx"}),
                "sheet_name": ("STRING", {"default": "Sheet1"}),
                "search_content": ("STRING", {"default": "查找内容"}),
                "search_mode": (["精确查找", "模糊查找"], {"default": "精确查找"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING", "INT", "INT")
    FUNCTION = "find_excel_data"
    CATEGORY = "Meeeyo/File"

    def IS_CHANGED():
        return float("NaN")

    def find_excel_data(self, excel_path, sheet_name, search_content, search_mode):
        try:
            if not os.path.exists(excel_path):
                return (f"Error: File does not exist at path: {excel_path}", None, None)

            if not os.access(excel_path, os.R_OK):
                return (f"Error: No read permission for file at path: {excel_path}", None, None)

            workbook = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
            sheet = workbook[sheet_name]

            results = []
            found_row = None
            found_col = None

            for row in range(1, sheet.max_row + 1):
                for col in range(1, sheet.max_column + 1):
                    cell = sheet.cell(row=row, column=col)
                    cell_value = cell.value if cell.value is not None else ""

                    if (search_mode == "精确查找" and cell_value == search_content) or \
                       (search_mode == "模糊查找" and search_content in cell_value):
                        results.append(f"{sheet_name}|{row}|{col}|{cell_value}")
                        found_row = row 
                        found_col = col

            workbook.close()
            del workbook

            if not results:
                return ("No results found.", None, None)

            return ("\n".join(results), found_row, found_col)

        except Exception as e:
            return (f"Error: {str(e)}", None, None)


#======读取表格数量差
class ReadExcelRowOrColumnDiff:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "excel_path": ("STRING", {"default": "path/to/your/file.xlsx"}),
                "sheet_name": ("STRING", {"default": "Sheet1"}),
                "read_mode": (["读行", "读列"], {"default": "读行"}),
                "indices": ("STRING", {"default": "1,3"}),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "read_excel_row_or_column_diff"
    CATEGORY = "Meeeyo/File"

    def IS_CHANGED():
        return float("NaN")

    def read_excel_row_or_column_diff(self, excel_path, sheet_name, read_mode, indices):
        try:
            if not os.path.exists(excel_path):
                return (f"Error: File does not exist at path: {excel_path}",)

            if not os.access(excel_path, os.R_OK):
                return (f"Error: No read permission for file at path: {excel_path}",)

            workbook = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
            sheet = workbook[sheet_name]

            def count_cells(mode, index):
                count = 0
                if mode == "读行":
                    for col in range(1, sheet.max_column + 1):
                        cell_value = sheet.cell(row=index, column=col).value
                        if cell_value is not None:
                            count += 1
                        else:
                            break
                elif mode == "读列":
                    for row in range(1, sheet.max_row + 1):
                        cell_value = sheet.cell(row=row, column=index).value
                        if cell_value is not None:
                            count += 1
                        else:
                            break
                return count

            indices = indices.strip()
            if "," in indices:
                try:
                    index1, index2 = map(int, indices.split(","))
                except ValueError:
                    return (f"Error: Invalid indices format. Please use 'number,number' format.",)

                count1 = count_cells(read_mode, index1)
                count2 = count_cells(read_mode, index2)
                result = count1 - count2
            else:
                try:
                    index = int(indices)
                except ValueError:
                    return (f"Error: Invalid index format. Please enter a valid number.",)

                result = count_cells(read_mode, index)

            workbook.close()
            del workbook

            return (result,)

        except Exception as e:
            return (f"Error: {str(e)}",)