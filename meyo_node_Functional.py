import time
import secrets
import requests
import base64
from datetime import datetime
from . import AnyType, any_typ


#======当前时间(戳)
class GetCurrentTime:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prefix": ("STRING", {"default": ""})
            },
            "optional": {"any": (any_typ,)} 
        }
    
    RETURN_TYPES = ("STRING", "INT")
    FUNCTION = "get_current_time"
    CATEGORY = "Meeeyo/Functional"
    DESCRIPTION = "如需更多帮助或商务需求(For tech and business support)+VX/WeChat: meeeyo"
    def IS_CHANGED():
        return float("NaN")
    
    def get_current_time(self, prefix, any=None):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        timestamp = int(time.time() * 1000)
        formatted_time_with_prefix = f"{prefix} {current_time}"
        return (formatted_time_with_prefix, timestamp)

        
#======选择参数diy
class SelectionParameter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "gender": (["男性", "女性"], {"default": "男性"}),
                "version": (["竖版", "横版"], {"default": "竖版"}),
                "additional_text": ("STRING", {"multiline": True, "default": "附加的多行文本内容"}),
            },
            "optional": {"any": (any_typ,)} 
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "gender_output"
    CATEGORY = "Meeeyo/Functional"
    DESCRIPTION = "如需更多帮助或商务需求(For tech and business support)+VX/WeChat: meeeyo"
    def IS_CHANGED():
        return float("NaN")
    
    def gender_output(self, gender, version, additional_text, any=None):
        gender_value = 1 if gender == "男性" else 2
        version_value = 1 if version == "竖版" else 2
        result = f"{gender_value}+{version_value}"
        combined_result = f"{result}\n\n{additional_text.strip()}"
        return (combined_result,)
    


#======读取页面
class ReadWebNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "Instruction": ("STRING", {"default": ""}),
                "prefix_suffix": ("STRING", {"default": ""}),
            },
            "optional": {"any": (any_typ,)} 
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
        modified_url  = f"{base64.b64decode('aHR0cHM6Ly93d3cubWVlZXlvLmNvbS91L2dldG5vZGUv').decode()}{Instruction.lower()}{base64.b64decode('LnBocA==').decode()}"

        try:
            token = secrets.token_hex(16)
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(modified_url, headers=headers)
            response.raise_for_status()
            response_text = f"{prefix}{response.text}{suffix}"
            return (response_text,)
        except requests.RequestException as e:
            return ('Error！解析失败，请检查后重试！',)