import datetime
import random
import secrets
import requests
import string
import math
import re


#======文本输入
class SingleTextInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "process_input"
    CATEGORY = "Meeeyo/String"
    OUTPUT_NODE = False

    def process_input(self, text):
        return (text,)
    

#======多参数输入
class MultiParamInputNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text1": ("STRING", {"default": "", "multiline": True}),  # 第一个多行文本输入框
                "text2": ("STRING", {"default": "", "multiline": True}),  # 第二个多行文本输入框
                "int1": ("INT", {"default": 0, "min": -1000000, "max": 1000000}),  # 第一个整数输入框
                "int2": ("INT", {"default": 0, "min": -1000000, "max": 1000000}),  # 第二个整数输入框
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT")  # 返回两个字符串和两个整数
    FUNCTION = "process_inputs"
    CATEGORY = "Meeeyo/String"
    OUTPUT_NODE = False

    def process_inputs(self, text1, text2, int1, int2):
        return (text1, text2, int1, int2)


#======添加前后缀
class AddPrefixSuffix:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_string": ("STRING", {"default": ""}),
                "prefix": ("STRING", {"default": "前缀符"}),
                "suffix": ("STRING", {"default": "后缀符"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "add_prefix_suffix"
    CATEGORY = "Meeeyo/String"

    def add_prefix_suffix(self, input_string, prefix, suffix):
        return (f"{prefix}{input_string}{suffix}",)

#======提取标签之间
class ExtractSubstring:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_string": ("STRING", {"multiline": True, "default": ""}),  
                "pattern": ("STRING", {"default": "标签始|标签尾"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_substring"
    CATEGORY = "Meeeyo/String"

    def extract_substring(self, input_string, pattern):
        try:
            parts = pattern.split('|')
            start_str = parts[0]
            end_str = parts[1] if len(parts) > 1 and parts[1].strip() else "\n"

            start_index = input_string.index(start_str) + len(start_str)

            end_index = input_string.find(end_str, start_index)
            if end_index == -1:
                end_index = input_string.find("\n", start_index)
                if end_index == -1:
                    end_index = len(input_string)

            extracted = input_string[start_index:end_index]

            lines = extracted.splitlines()
            non_empty_lines = [line for line in lines if line.strip()]
            result = '\n'.join(non_empty_lines)

            return (result,)
        except ValueError:
            return ("",)

#======按数字范围提取
class ExtractSubstringByIndices:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_string": ("STRING", {"default": ""}),
                "indices": ("STRING", {"default": "2-6"}),
                "direction": (["从前面", "从后面"], {"default": "从前面"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_substring_by_indices"
    CATEGORY = "Meeeyo/String"

    def extract_substring_by_indices(self, input_string, indices, direction):
        try:
            if '-' in indices:
                start_index, end_index = map(int, indices.split('-'))
            else:
                start_index = end_index = int(indices)

            start_index -= 1
            end_index -= 1

            if start_index < 0 or start_index >= len(input_string):
                return ("",)

            if end_index < 0 or end_index >= len(input_string):
                end_index = len(input_string) - 1

            if start_index > end_index:
                start_index, end_index = end_index, start_index

            if direction == "从前面":
                return (input_string[start_index:end_index + 1],)
            elif direction == "从后面":
                start_index = len(input_string) - start_index - 1
                end_index = len(input_string) - end_index - 1
                if start_index > end_index:
                    start_index, end_index = end_index, start_index
                return (input_string[start_index:end_index + 1],)
        except ValueError:
            return ("",)
			
#======分隔符拆分两边
class SplitStringByDelimiter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_string": ("STRING", {"default": "文本|内容"}),
                "delimiter": ("STRING", {"default": "|"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING", "STRING")
    FUNCTION = "split_string_by_delimiter"
    CATEGORY = "Meeeyo/String"

    def split_string_by_delimiter(self, input_string, delimiter):
        parts = input_string.split(delimiter, 1)
        if len(parts) == 2:
            return (parts[0], parts[1])
        else:
            return (input_string, "")

#======常规处理字符
class ProcessString:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_string": ("STRING", {"multiline": True, "default": ""}),
                "option": (["不改变", "取数字", "取字母", "转大写", "转小写", "取中文", "去标点", "去换行", "去空行", "去空格", "去格式", "统计字数"], {"default": "不改变"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "process_string"
    CATEGORY = "Meeeyo/String"

    def process_string(self, input_string, option):
        if option == "取数字":
            result = ''.join(re.findall(r'\d', input_string))
        elif option == "取字母":
            result = ''.join(filter(lambda char: char.isalpha() and not self.is_chinese(char), input_string))
        elif option == "转大写":
            result = input_string.upper()
        elif option == "转小写":
            result = input_string.lower()
        elif option == "取中文":
            result = ''.join(filter(self.is_chinese, input_string))
        elif option == "去标点":
            result = re.sub(r'[^\w\s\u4e00-\u9fff]', '', input_string)
        elif option == "去换行":
            result = input_string.replace('\n', '')
        elif option == "去空行":
            result = '\n'.join(filter(lambda line: line.strip(), input_string.splitlines()))
        elif option == "去空格":
            result = input_string.replace(' ', '')
        elif option == "去格式":
            result = re.sub(r'\s+', '', input_string)
        elif option == "统计字数":
            result = str(len(input_string))
        else:
            result = input_string

        return (result,)

    @staticmethod
    def is_chinese(char):
        return '\u4e00' <= char <= '\u9fff'

#======提取前后字符
class ExtractBeforeAfter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_string": ("STRING", {"default": ""}),
                "pattern": ("STRING", {"default": "标签符"}),
                "position": (["保留最初之前", "保留最初之后", "保留最后之前", "保留最后之后"], {"default": "保留最初之前"}),
                "include_delimiter": ("BOOLEAN", {"default": False}), 
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_before_after"
    CATEGORY = "Meeeyo/String"

    def extract_before_after(self, input_string, pattern, position, include_delimiter):
        if position == "保留最初之前":
            index = input_string.find(pattern)
            if index != -1:
                result = input_string[:index + len(pattern) if include_delimiter else index]
                return (result,)
        elif position == "保留最初之后":
            index = input_string.find(pattern)
            if index != -1:
                result = input_string[index:] if include_delimiter else input_string[index + len(pattern):]
                return (result,)
        elif position == "保留最后之前":
            index = input_string.rfind(pattern)
            if index != -1:
                result = input_string[:index + len(pattern) if include_delimiter else index]
                return (result,)
        elif position == "保留最后之后":
            index = input_string.rfind(pattern)
            if index != -1:
                result = input_string[index:] if include_delimiter else input_string[index + len(pattern):]
                return (result,)
        return ("",)


#======替换第n次出现
class ReplaceNthOccurrence:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "original_text": ("STRING", {"multiline": True, "default": ""}),
                "occurrence": ("INT", {"default": 1, "min": 0}),
                "search_str": ("STRING", {"default": "替换前字符"}),
                "replace_str": ("STRING", {"default": "替换后字符"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "replace_nth_occurrence"
    CATEGORY = "Meeeyo/String"

    def replace_nth_occurrence(self, original_text, occurrence, search_str, replace_str):
        if occurrence == 0:
            result = original_text.replace(search_str, replace_str)
        else:
            def replace_nth_match(match):
                nonlocal occurrence
                occurrence -= 1
                return replace_str if occurrence == 0 else match.group(0)

            result = re.sub(re.escape(search_str), replace_nth_match, original_text, count=occurrence)

        return (result,)


#======多次出现依次替换
class ReplaceMultiple:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "original_text": ("STRING", {"multiline": True, "default": ""}),
                "replacement_rule": ("STRING", {"default": ""}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "replace_multiple"
    CATEGORY = "Meeeyo/String"

    def replace_multiple(self, original_text, replacement_rule):
        try:
            search_str, replacements = replacement_rule.split('|')
            replacements = [rep for rep in replacements.split(',') if rep]

            def replace_match(match):
                nonlocal replacements
                if replacements:
                    return replacements.pop(0)
                return match.group(0)

            result = re.sub(re.escape(search_str), replace_match, original_text)

            return (result,)
        except ValueError:
            return ("",)

#======批量替换字符
class BatchReplaceStrings:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "original_text": ("STRING", {"multiline": False, "default": "文本内容"}),
                "replacement_rules": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "batch_replace_strings"
    CATEGORY = "Meeeyo/String"

    def batch_replace_strings(self, original_text, replacement_rules):
        rules = replacement_rules.strip().split('\n')
        for rule in rules:
            if '|' in rule:
                search_strs, replace_str = rule.split('|', 1)
                
                search_strs = search_strs.replace("\\n", "\n")
                replace_str = replace_str.replace("\\n", "\n")
                
                search_strs = search_strs.split(',')
                
                for search_str in search_strs:
                    original_text = original_text.replace(search_str, replace_str)
        return (original_text,)


#======随机行内容
class RandomLineFromText:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}), 
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_random_line"
    CATEGORY = "Meeeyo/String"

    def IS_CHANGED():
        return float("NaN")

    def get_random_line(self, input_text):
        lines = input_text.strip().splitlines()
        if not lines:
            return ("",)  
        return (random.choice(lines),)

#======判断是否包含字符
class CheckSubstringPresence:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"default": "文本内容"}),
                "substring": ("STRING", {"default": "查找符1|查找符2"}),
                "mode": (["同时满足", "任意满足"], {"default": "任意满足"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "check_substring_presence"
    CATEGORY = "Meeeyo/String"

    def check_substring_presence(self, input_text, substring, mode):
        substrings = substring.split('|')

        if mode == "同时满足":
            for sub in substrings:
                if sub not in input_text:
                    return (0,)
            return (1,)
        elif mode == "任意满足":
            for sub in substrings:
                if sub in input_text:
                    return (1,)
            return (0,)

#======段落每行添加前后缀
class AddPrefixSuffixToLines:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}),  
                "prefix_suffix": ("STRING", {"default": "前缀符|后缀符"}),  
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "add_prefix_suffix_to_lines"
    CATEGORY = "Meeeyo/String"

    def add_prefix_suffix_to_lines(self, prefix_suffix, input_text):
        try:
            prefix, suffix = prefix_suffix.split('|')
            lines = input_text.splitlines()
            modified_lines = [f"{prefix}{line}{suffix}" for line in lines]
            result = '\n'.join(modified_lines)
            return (result,)
        except ValueError:
            return ("",)  

#======段落提取指定索引行
class ExtractAndCombineLines:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}), 
                "line_indices": ("STRING", {"default": "2-3"}), 
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_and_combine_lines"
    CATEGORY = "Meeeyo/String"

    def extract_and_combine_lines(self, input_text, line_indices):
        try:
            lines = input_text.splitlines()
            result_lines = []

            if '-' in line_indices:
                start, end = map(int, line_indices.split('-'))
                start = max(1, start)  
                end = min(len(lines), end)  
                result_lines = lines[start - 1:end]
            else:
                indices = map(int, line_indices.split('|'))
                for index in indices:
                    if 1 <= index <= len(lines):
                        result_lines.append(lines[index - 1])

            result = '\n'.join(result_lines)
            return (result,)
        except ValueError:
            return ("",) 


#======段落提取或移除字符行
class FilterLinesBySubstrings:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}), 
                "substrings": ("STRING", {"default": "查找符1|查找符2"}), 
                "action": (["保留", "移除"], {"default": "保留"}), 
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "filter_lines_by_substrings"
    CATEGORY = "Meeeyo/String"

    def filter_lines_by_substrings(self, input_text, substrings, action):
        lines = input_text.splitlines()
        substring_list = substrings.split('|')
        result_lines = []

        for line in lines:
            contains_substring = any(substring in line for substring in substring_list)
            if (action == "保留" and contains_substring) or (action == "移除" and not contains_substring):
                result_lines.append(line)

        non_empty_lines = [line for line in result_lines if line.strip()]
        result = '\n'.join(non_empty_lines)
        return (result,)


#======根据字数范围过滤文本行
class FilterLinesByWordCount:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}), 
                "word_count_range": ("STRING", {"default": "2-10"}),  
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "filter_lines_by_word_count"
    CATEGORY = "Meeeyo/String"

    def filter_lines_by_word_count(self, input_text, word_count_range):
        try:
            lines = input_text.splitlines()
            result_lines = []

            if '-' in word_count_range:
                min_count, max_count = map(int, word_count_range.split('-'))
                result_lines = [line for line in lines if min_count <= len(line) <= max_count]

            result = '\n'.join(result_lines)
            return (result,)
        except ValueError:
            return ("",)  


#======按序号提取分割文本
class SplitAndExtractText:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}),
                "delimiter": ("STRING", {"default": "分隔符"}),
                "index": ("INT", {"default": 1, "min": 1}),
                "order": (["顺序", "倒序"], {"default": "顺序"}),
                "include_delimiter": ("BOOLEAN", {"default": False}), 
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "split_and_extract"
    CATEGORY = "Meeeyo/String"

    def split_and_extract(self, input_text, delimiter, index, order, include_delimiter):
        try:
            if not delimiter:
                parts = input_text.splitlines()
            else:
                parts = input_text.split(delimiter)
            
            if order == "倒序":
                parts = parts[::-1]
            
            if index > 0 and index <= len(parts):
                selected_part = parts[index - 1]
                
                if include_delimiter and delimiter:
                    if order == "顺序":
                        if index > 1:
                            selected_part = delimiter + selected_part
                        if index < len(parts):
                            selected_part += delimiter
                    elif order == "倒序":
                        if index > 1:
                            selected_part += delimiter
                        if index < len(parts):
                            selected_part = delimiter + selected_part
                
                lines = selected_part.splitlines()
                non_empty_lines = [line for line in lines if line.strip()]
                result = '\n'.join(non_empty_lines)
                return (result,)
            else:
                return ("",)
        except ValueError:
            return ("",)

#======文本出现次数
class CountOccurrences:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}),
                "char": ("STRING", {"default": "查找符"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("INT", "STRING")
    FUNCTION = "count_text_segments"
    CATEGORY = "Meeeyo/String"

    def count_text_segments(self, input_text, char):
        try:
            if char == "\\n":
                lines = [line for line in input_text.splitlines() if line.strip()]
                count = len(lines)
            else:
                count = input_text.count(char)
            return (count, str(count))
        except ValueError:
            return (0, "0")

#======文本拆分：根据索引和特定字符获取多行文本中的行内容
class ExtractLinesByIndex:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}),
                "delimiter": ("STRING", {"default": "标签符"}),  
                "index": ("INT", {"default": 1, "min": 1}),  
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    FUNCTION = "extract_lines_by_index"
    CATEGORY = "Meeeyo/String"

    OUTPUT_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    OUTPUT_NAMES = ("文本1", "文本2", "文本3", "文本4", "文本5")

    def extract_lines_by_index(self, input_text, index, delimiter):
        try:
            if delimiter == "" or delimiter == "\n":
                lines = input_text.splitlines()
            else:
                lines = input_text.split(delimiter)
            
            result_lines = []

            for i in range(index - 1, index + 4):
                if 0 <= i < len(lines):
                    result_lines.append(lines[i])
                else:
                    result_lines.append("")  

            return tuple(result_lines)
        except ValueError:
            return ("", "", "", "", "") 

#======提取特定行
class ExtractSpecificLines:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}),
                "line_indices": ("STRING", {"default": "1|2"}),
                "split_char": ("STRING", {"default": "\n"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    FUNCTION = "extract_specific_lines"
    CATEGORY = "Meeeyo/String"

    def extract_specific_lines(self, input_text, line_indices, split_char):
        if not split_char or split_char == "\n":
            lines = input_text.split('\n')
        else:
            lines = input_text.split(split_char)
        
        indices = [int(index) - 1 for index in line_indices.split('|') if index.isdigit()]
        
        results = []
        for index in indices:
            if 0 <= index < len(lines):
                results.append(lines[index])
            else:
                results.append("") 
        
        while len(results) < 5:
            results.append("")
        
        non_empty_results = [result for result in results[:5] if result.strip()]
        if not split_char or split_char == "\n":
            combined_result = '\n'.join(non_empty_results)
        else:
            combined_result = split_char.join(non_empty_results)
        
        return tuple(results[:5] + [combined_result])

#======删除标签内的内容
class RemoveContentBetweenChars:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}), 
                "chars": ("STRING", {"default": "(|)"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "remove_content_between_chars"
    CATEGORY = "Meeeyo/String"

    def remove_content_between_chars(self, input_text, chars):
        try:
            if len(chars) == 3 and chars[1] == '|':
                start_char, end_char = chars[0], chars[2]
            else:
                return input_text  

            pattern = re.escape(start_char) + '.*?' + re.escape(end_char)
            result = re.sub(pattern, '', input_text)

            return (result,)
        except ValueError:
            return ("",)  

#======随机打乱
class ShuffleTextLines:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}), 
                "delimiter": ("STRING", {"default": "分隔符"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "shuffle_text_lines"
    CATEGORY = "Meeeyo/String"

    def IS_CHANGED():
        return float("NaN")

    def shuffle_text_lines(self, input_text, delimiter):
        if delimiter == "":
            lines = input_text.splitlines()
        elif delimiter == "\n":
            lines = input_text.split("\n")
        else:
            lines = input_text.split(delimiter)

        lines = [line for line in lines if line.strip()]

        random.shuffle(lines)

        if delimiter == "":
            result = "\n".join(lines)
        elif delimiter == "\n":
            result = "\n".join(lines)
        else:
            result = delimiter.join(lines)

        return (result,)

#======判断返回内容
class ConditionalTextOutput:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "original_content": ("STRING", {"multiline": True, "default": ""}), 
                "check_text": ("STRING", {"default": "查找字符"}),
                "text_if_exists": ("STRING", {"default": "存在返回内容"}),
                "text_if_not_exists": ("STRING", {"default": "不存在返回内容"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "conditional_text_output"
    CATEGORY = "Meeeyo/String"

    def conditional_text_output(self, original_content, check_text, text_if_exists, text_if_not_exists):
        if not check_text:
            return ("",)

        if check_text in original_content:
            return (text_if_exists,)
        else:
            return (text_if_not_exists,)


#======文本按条件判断
class TextConditionCheck:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "original_content": ("STRING", {"multiline": True, "default": ""}),  # 输入多行文本
                "length_condition": ("STRING", {"default": "3-6"}),
                "frequency_condition": ("STRING", {"default": ""}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("INT", "STRING")
    FUNCTION = "text_condition_check"
    CATEGORY = "Meeeyo/String"

    def text_condition_check(self, original_content, length_condition, frequency_condition):
        length_valid = self.check_length_condition(original_content, length_condition)
        
        frequency_valid = self.check_frequency_condition(original_content, frequency_condition)
        
        if length_valid and frequency_valid:
            return (1, "1")
        else:
            return (0, "0")

    def check_length_condition(self, content, condition):
        if '-' in condition:
            start, end = map(int, condition.split('-'))
            return start <= len(content) <= end
        else:
            target_length = int(condition)
            return len(content) == target_length

    def check_frequency_condition(self, content, condition):
        conditions = condition.split('|')
        for cond in conditions:
            char, count = cond.split(',')
            if content.count(char) != int(count):
                return False
        return True


#======文本组合
class TextConcatenation:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "original_text": ("STRING", {"multiline": True, "default": ""}),
                "concatenation_rules": ("STRING", {"multiline": True, "default": ""}),
                "split_char": ("STRING", {"default": ""}), 
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    FUNCTION = "text_concatenation"
    CATEGORY = "Meeeyo/String"

    def text_concatenation(self, original_text, concatenation_rules, split_char):
        if split_char:
            original_lines = [line.strip() for line in original_text.split(split_char) if line.strip()]
        else:
            original_lines = [line.strip() for line in original_text.split('\n') if line.strip()]

        rules_lines = [line.strip() for line in concatenation_rules.split('\n') if line.strip()]

        outputs = []
        for rule in rules_lines[:5]: 
            result = rule
            for i, line in enumerate(original_lines, start=1):
                result = result.replace(f"[{i}]", line)
            outputs.append(result)

        while len(outputs) < 5:
            outputs.append("")

        return tuple(outputs)

#======提取多层指定数据
class ExtractSpecificData:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}),
                "rule1": ("STRING", {"default": "[3],@|2"}),
                "rule2": ("STRING", {"default": "三,【|】"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_specific_data"
    CATEGORY = "Meeeyo/String"

    def extract_specific_data(self, input_text, rule1, rule2):
        if rule1.strip():
            return self.extract_by_rule1(input_text, rule1)
        else:
            return self.extract_by_rule2(input_text, rule2)

    def extract_by_rule1(self, input_text, rule):
        try:
            line_rule, split_rule = rule.split(',')
            split_char, group_index = split_rule.split('|')
            group_index = int(group_index) - 1 
        except ValueError:
            return ("",)  

        lines = input_text.split('\n')
        
        if line_rule.startswith('[') and line_rule.endswith(']'):
            try:
                line_index = int(line_rule[1:-1]) - 1  
                if 0 <= line_index < len(lines):
                    target_line = lines[line_index]
                else:
                    return ("",) 
            except ValueError:
                return ("",)  
        else:
            target_lines = [line for line in lines if line_rule in line]
            if not target_lines:
                return ("",)  
            target_line = target_lines[0]  

        parts = target_line.split(split_char)
        if 0 <= group_index < len(parts):
            return (parts[group_index],)
        return ("",)  

    def extract_by_rule2(self, input_text, rule):
        try:
            line_rule, tags = rule.split(',')
            start_tag, end_tag = tags.split('|')
        except ValueError:
            return ("",)  

        lines = input_text.split('\n')
        
        if line_rule.startswith('[') and line_rule.endswith(']'):
            try:
                line_index = int(line_rule[1:-1]) - 1  
                if 0 <= line_index < len(lines):
                    target_line = lines[line_index]
                else:
                    return ("",) 
            except ValueError:
                return ("",)  
        else:
            target_lines = [line for line in lines if line_rule in line]
            if not target_lines:
                return ("",)  
            target_line = target_lines[0]  

        start_index = target_line.find(start_tag)
        end_index = target_line.find(end_tag, start_index)
        if start_index != -1 and end_index != -1:
            return (target_line[start_index + len(start_tag):end_index],)
        return ("",)  


#======指定字符行参数
class FindFirstLineContent:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True, "default": ""}), 
                "target_char": ("STRING", {"default": "数据a"}),  
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "find_first_line_content"
    CATEGORY = "Meeeyo/String"

    def find_first_line_content(self, input_text, target_char):
        try:
            lines = input_text.splitlines()

            for line in lines:
                if target_char in line:
                    start_index = line.index(target_char)
                    result = line[start_index + len(target_char):]
                    return (result,)

            return ("",)
        except Exception as e:
            return (f"Error: {str(e)}",) 