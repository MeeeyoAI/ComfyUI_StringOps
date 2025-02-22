import csv
import openpyxl
import os


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