import os
import csv
import torch
import shutil
import requests
import chardet
import pathlib
import openpyxl
import folder_paths
import node_helpers
import numpy as np
from PIL import Image, ImageOps, ImageSequence
from pathlib import Path

#======加载重置图像
class LoadAndAdjustImage:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f.name for f in Path(input_dir).iterdir() if f.is_file()]
        return {
            "required": {
                "image": (sorted(files), {"image_upload": True}),
                "max_dimension": ("INT", {"default": 1024, "min": 0, "max": 4096, "step": 8}),
                "size_option": (["Custom", "Small", "Medium", "Large"], {"default": "Custom"})
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "info")
    FUNCTION = "load_image"
    CATEGORY = "Meeeyo/File"
    
    def IS_CHANGED():
        return float("NaN")

    def load_image(self, image, max_dimension, size_option):
        image_path = folder_paths.get_annotated_filepath(image)
        img = Image.open(image_path)
        W, H = img.size
        aspect_ratio = W / H

        def get_target_size():
            if size_option == "Custom":
                ratio = min(max_dimension / W, max_dimension / H)
                return round(W * ratio), round(H * ratio)
            
            size_options = {
                "Small": (
                    (768, 512) if aspect_ratio >= 1.23 else
                    (512, 768) if aspect_ratio <= 0.82 else
                    (768, 768)
                ),
                "Medium": (
                    (1216, 832) if aspect_ratio >= 1.23 else
                    (832, 1216) if aspect_ratio <= 0.82 else
                    (1216, 1216)
                ),
                "Large": (
                    (1600, 1120) if aspect_ratio >= 1.23 else
                    (1120, 1600) if aspect_ratio <= 0.82 else
                    (1600, 1600)
                )
            }
            return size_options[size_option]
        target_width, target_height = get_target_size()
        output_images = []
        output_masks = []

        for frame in ImageSequence.Iterator(img):
            frame = ImageOps.exif_transpose(frame)
            if frame.mode == 'P':
                frame = frame.convert("RGBA")
            elif 'A' in frame.getbands():
                frame = frame.convert("RGBA")
            if size_option == "Custom":
                ratio = min(target_width / W, target_height / H)
                adjusted_width = round(W * ratio)
                adjusted_height = round(H * ratio)
                image_frame = frame.convert("RGB").resize((adjusted_width, adjusted_height), Image.Resampling.BILINEAR)
            else:
                image_frame = frame.convert("RGB")
                image_frame = ImageOps.fit(image_frame, (target_width, target_height), method=Image.Resampling.BILINEAR, centering=(0.5, 0.5))
            image_array = np.array(image_frame).astype(np.float32) / 255.0
            output_images.append(torch.from_numpy(image_array)[None,])
            if 'A' in frame.getbands():
                mask_frame = frame.getchannel('A')
                if size_option == "Custom":
                    mask_frame = mask_frame.resize((adjusted_width, adjusted_height), Image.Resampling.BILINEAR)
                else:
                    mask_frame = ImageOps.fit(mask_frame, (target_width, target_height), method=Image.Resampling.BILINEAR, centering=(0.5, 0.5))
                mask = np.array(mask_frame).astype(np.float32) / 255.0
                mask = 1. - mask
            else:
                if size_option == "Custom":
                    mask = np.zeros((adjusted_height, adjusted_width), dtype=np.float32)
                else:
                    mask = np.zeros((target_height, target_width), dtype=np.float32)
            output_masks.append(torch.from_numpy(mask).unsqueeze(0))
        output_image = torch.cat(output_images, dim=0) if len(output_images) > 1 else output_images[0]
        output_mask = torch.cat(output_masks, dim=0) if len(output_masks) > 1 else output_masks[0]
        info = f"Image Path: {image_path}\nOriginal Size: {W}x{H}\nAdjusted Size: {target_width}x{target_height}"
        return (output_image, output_mask, info)
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
    
    def IS_CHANGED():
        return float("NaN")

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

                size_options = {
                    "Small": (
                        (768, 512) if aspect_ratio >= 1.23 else
                        (512, 768) if aspect_ratio <= 0.82 else
                        (768, 768)
                    ),
                    "Medium": (
                        (1216, 832) if aspect_ratio >= 1.23 else
                        (832, 1216) if aspect_ratio <= 0.82 else
                        (1216, 1216)
                    ),
                    "Large": (
                        (1600, 1120) if aspect_ratio >= 1.23 else
                        (1120, 1600) if aspect_ratio <= 0.82 else
                        (1600, 1600)
                    )
                }

                target_width, target_height = size_options[size_option]
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
                "image_format": (["PNG", "JPG"], {"default": "JPG"})
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "save_image"
    OUTPUT_NODE = True
    CATEGORY = "Meeeyo/File"
    
    def IS_CHANGED():
        return float("NaN")

    def save_image(self, image, save_path, image_name, image_format):
        if not isinstance(image, torch.Tensor):
            raise ValueError("Invalid image tensor format")
        if save_path == "./output":
            save_path = self.output_dir
        elif not os.path.isabs(save_path):
            save_path = os.path.join(self.output_dir, save_path)
        os.makedirs(save_path, exist_ok=True)
        
        # 移除可能存在的扩展名，然后添加用户选择的格式对应的扩展名
        base_name = os.path.splitext(image_name)[0]
        
        batch_size = image.shape[0]
        channel_to_mode = {1: "L", 3: "RGB", 4: "RGBA"}

        for i in range(batch_size):
            # 根据选择的格式动态设置扩展名
            if image_format == "PNG":
                filename = f"{base_name}.png" if batch_size == 1 else f"{base_name}_{i:05d}.png"
                save_format = "PNG"
                save_params = {"compress_level": 0}
            else:  # JPG
                filename = f"{base_name}.jpg" if batch_size == 1 else f"{base_name}_{i:05d}.jpg"
                save_format = "JPEG"
                save_params = {"quality": 100}
            
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
            
            # 如果是JPG格式，需要转换为RGB模式
            if image_format == "JPG":
                pil_image = pil_image.convert("RGB")
            
            pil_image.save(full_path, format=save_format, **save_params)
        return (image,)


#======文件操作
class FileCopyCutNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "source_path": ("STRING", {"default": "", "multiline": False}),
                "destination_path": ("STRING", {"default": "", "multiline": False}),
                "operation": (["copy", "cut"], {"default": "copy"}),
            },
            "optional": {
                "any": ("*",), 
            },
        }
    
    RETURN_TYPES = ("STRING",)  # 返回操作结果字符串
    RETURN_NAMES = ("result",)
    FUNCTION = "copy_cut_file"
    CATEGORY = "Meeeyo/File"
    
    def IS_CHANGED():
        return float("NaN")

    def copy_cut_file(self, source_path, destination_path, operation, **kwargs):
        result = "执行失败"
        try:
            # 检查文件是否存在
            if not os.path.isfile(source_path):
                raise Exception(f"Source file not found: {source_path}")
                
            # 确保目录存在
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # 执行复制或剪切操作
            if operation == "copy":
                shutil.copy2(source_path, destination_path)
                result = "执行成功: 文件已复制"
            elif operation == "cut":
                shutil.move(source_path, destination_path)
                result = "执行成功: 文件已剪切"
        except Exception as e:
            result = f"执行失败: {str(e)}"
        
        return (result,)


#======读取页面
class ReadWebNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": "https://", "multiline": False}),
            },
            "optional": {
                "any": ("*",),  # 可选触发输入
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)
    FUNCTION = "read_web"
    CATEGORY = "Meeeyo/File"
    
    def IS_CHANGED():
        return float("NaN")

    def read_web(self, url, any=None):
        try:
            response = requests.get(url)
            encoding = chardet.detect(response.content)['encoding']
            response.encoding = encoding or 'ISO-8859-1'
            if response.status_code == 200:
                return (response.text,)
            else:
                return (f"Failed to retrieve webpage. Status code: {response.status_code}",)
        except Exception as e:
            return (f"Error: {str(e)}",)


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
