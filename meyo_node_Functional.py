import datetime
import time
import secrets
import requests
import base64


class GetCurrentTime:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prefix": ("STRING", {"default": ""}),
            },
            "optional": {
                "any": ("*",),
            },
        }

    RETURN_TYPES = ("STRING", "INT")
    FUNCTION = "get_current_time"
    CATEGORY = "Meeeyo/Functional"
    DESCRIPTION = "如需更多帮助或商务需求(For tech and business support)+VX/WeChat: meeeyo"
    
    def IS_CHANGED():
        return float("NaN")

    def get_current_time(self, prefix="", any=None):
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        result = f"{prefix}{formatted_time}"
        timestamp = int(round(time.time() * 1000))
        return (result, timestamp)
        

class SelectionParameter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "gender": (["男性", "女性"], {"default": "男性"}),
                "version": (["竖版", "横版"], {"default": "竖版"}),
                "additional_text": ("STRING", {"multiline": True, "default": "附加的多行文本内容"}),
            },
            "optional": {},
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "gender_output"
    CATEGORY = "Meeeyo/Functional"
    DESCRIPTION = "如需更多帮助或商务需求(For tech and business support)+VX/WeChat: meeeyo"
    
    def gender_output(self, gender, version, additional_text):
        gender_value = 1 if gender == "男性" else 2
        version_value = 1 if version == "竖版" else 2
        result = f"{gender_value}+{version_value}"
        combined_result = f"{result}\n\n{additional_text.strip()}"
        return (combined_result,)
    

class ReadWebNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "Instruction": ("STRING", {"default": ""}),
                "prefix_suffix": ("STRING", {"default": ""}),
            },
            "optional": {
                "any": ("*",),
            },
            "hidden": {}
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "fetch_data"
    CATEGORY = "Meeeyo/Functional"
    DESCRIPTION = "如需更多帮助或商务需求(For tech and business support)+VX/WeChat: meeeyo"
    
    def IS_CHANGED():
        return float("NaN")

    def fetch_data(self, Instruction, prefix_suffix, any=None):
        if "|" in prefix_suffix:
            prefix, suffix = prefix_suffix.split("|", 1)
        else:
            prefix = prefix_suffix
            suffix = ""
        modified_url  = f"{base64.b64decode('aHR0cHM6Ly93d3cubWVlZXlvLmNvbS8=').decode()}{Instruction.lower()}{base64.b64decode('LnBocA==').decode()}"

        try:
            token = secrets.token_hex(16)
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(modified_url, headers=headers)
            response.raise_for_status()
            response_text = f"{prefix}{response.text}{suffix}"
            return (response_text,)
        except requests.RequestException as e:
            return ('Error！解析失败，请检查后重试！',)