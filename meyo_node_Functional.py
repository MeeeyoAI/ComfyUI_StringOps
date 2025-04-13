import datetime
import time

#======获取当前时间
class GetCurrentTime:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prefix": ("STRING", {"default": ""}),  # Input field for the prefix
            },
            "optional": {
                "any": ("*",),  # Accept any type of input as optional
            },
        }

    RETURN_TYPES = ("STRING", "INT")  # 新增 INTEGER 类型的返回值
    FUNCTION = "get_current_time"
    CATEGORY = "Meeeyo/Functional"
    
    def IS_CHANGED():
        return float("NaN")

    def get_current_time(self, prefix="", any=None):
        # Get the current system time
        current_time = datetime.datetime.now()
        # Format the time as a string
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        # Include the prefix in the output
        result = f"{prefix}{formatted_time}"
        # Get the current timestamp as an integer with milliseconds precision
        timestamp = int(round(time.time() * 1000))  # 获取当前时间戳的整数部分并精确到毫秒
        # Return both the formatted time with prefix and the timestamp
        return (result, timestamp)  # 返回两个值：字符串和整数
        

#======选择性别和模板
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

    def gender_output(self, gender, version, additional_text):
        # 根据选择的性别返回相应的值
        gender_value = 1 if gender == "男性" else 2
        version_value = 1 if version == "竖版" else 2

        # 组合成最终的输出格式 "1+1" 或 "1+2" 或 "2+1" 或 "2+2"
        result = f"{gender_value}+{version_value}"

        # 将生成的整数组合与多行文本内容合并输出
        combined_result = f"{result}\n\n{additional_text.strip()}"
        return (combined_result,)