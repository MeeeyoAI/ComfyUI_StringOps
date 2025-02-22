from .meyo_node_Computational import StandardSize, CompareInt, FloatToInteger, GenerateNumbers, GetRandomIntegerInRange
from .meyo_node_String import AddPrefixSuffix, ExtractSubstring, ExtractSubstringByIndices, SplitStringByDelimiter, ProcessString, ExtractBeforeAfter, ReplaceNthOccurrence, BatchReplaceStrings, ReplaceMultiple, RandomLineFromText, CheckSubstringPresence, AddPrefixSuffixToLines, ExtractAndCombineLines, FilterLinesBySubstrings, FilterLinesByWordCount, SplitAndExtractText, CountOccurrences, ExtractLinesByIndex, ExtractSpecificLines, RemoveContentBetweenChars, ShuffleTextLines, ConditionalTextOutput, TextConditionCheck, TextConcatenation, ExtractSpecificData, FindFirstLineContent
from .meyo_node_File import FileListAndSuffix, ReadExcelData, WriteExcelData, FindExcelData, ReadExcelRowOrColumnDiff


NODE_CLASS_MAPPINGS = {

    #运算型节点：meyo_node_Computational
    "StandardSize": StandardSize,
    "CompareInt": CompareInt,
    "FloatToInteger": FloatToInteger,
    "GenerateNumbers": GenerateNumbers,
    "GetRandomIntegerInRange": GetRandomIntegerInRange,

    #字符串处理：meyo_node_String
    "AddPrefixSuffix": AddPrefixSuffix,
    "ExtractSubstring": ExtractSubstring,
    "ExtractSubstringByIndices": ExtractSubstringByIndices,
    "SplitStringByDelimiter": SplitStringByDelimiter,
    "ProcessString": ProcessString,
    "ExtractBeforeAfter": ExtractBeforeAfter,
    "ReplaceNthOccurrence": ReplaceNthOccurrence,
    "ReplaceMultiple": ReplaceMultiple,
    "BatchReplaceStrings": BatchReplaceStrings,
    "RandomLineFromText": RandomLineFromText,
    "CheckSubstringPresence": CheckSubstringPresence,
    "AddPrefixSuffixToLines": AddPrefixSuffixToLines,
    "ExtractAndCombineLines": ExtractAndCombineLines,
    "FilterLinesBySubstrings": FilterLinesBySubstrings,
    "FilterLinesByWordCount": FilterLinesByWordCount,
    "SplitAndExtractText": SplitAndExtractText,
    "CountOccurrences": CountOccurrences,
    "ExtractLinesByIndex": ExtractLinesByIndex,
    "ExtractSpecificLines": ExtractSpecificLines,
    "RemoveContentBetweenChars": RemoveContentBetweenChars,
    "ShuffleTextLines": ShuffleTextLines,
    "ConditionalTextOutput": ConditionalTextOutput,
    "TextConditionCheck": TextConditionCheck,
    "TextConcatenation": TextConcatenation,
    "ExtractSpecificData": ExtractSpecificData,
    "FindFirstLineContent": FindFirstLineContent,

    #文件处理：meyo_node_File
    "FileListAndSuffix": FileListAndSuffix,
    "ReadExcelData": ReadExcelData,
    "WriteExcelData": WriteExcelData,
    "FindExcelData": FindExcelData,
    "ReadExcelRowOrColumnDiff": ReadExcelRowOrColumnDiff,

}


NODE_DISPLAY_NAME_MAPPINGS = {

   #运算型节点：meyo_node_Computational
   "StandardSize": "重置尺寸(meeeyo.com)",
   "CompareInt": "比较数值(meeeyo.com)",
   "FloatToInteger": "规范数值(meeeyo.com)",
   "GenerateNumbers": "生成范围数组(meeeyo.com)",
   "GetRandomIntegerInRange": "范围内随机数(meeeyo.com)",

   #字符串处理：meyo_node_String
   "AddPrefixSuffix": "添加前后缀(meeeyo.com)",
   "ExtractSubstring": "提取标签之间(meeeyo.com)",
   "ExtractSubstringByIndices": "按数字范围提取(meeeyo.com)",
   "SplitStringByDelimiter": "分隔符拆分两边(meeeyo.com)",
   "ProcessString": "常规处理字符(meeeyo.com)",
   "ExtractBeforeAfter": "提取前后字符(meeeyo.com)",
   "ReplaceNthOccurrence": "替换第n次出现(meeeyo.com)",
   "ReplaceMultiple": "多次出现依次替换(meeeyo.com)",
   "BatchReplaceStrings": "批量替换字符(meeeyo.com)",
   "RandomLineFromText": "随机行内容(meeeyo.com)",
   "CheckSubstringPresence": "判断是否包含字符(meeeyo.com)",
   "AddPrefixSuffixToLines": "段落每行添加前后缀(meeeyo.com)",
   "ExtractAndCombineLines": "段落提取指定索引行(meeeyo.com)",
   "FilterLinesBySubstrings": "段落提取或移除字符行(meeeyo.com)",
   "FilterLinesByWordCount": "段落字数条件过滤行(meeeyo.com)",
   "SplitAndExtractText": "按序号提取分割文本(meeeyo.com)",
   "CountOccurrences": "文本出现次数(meeeyo.com)",
   "ExtractLinesByIndex": "文本拆分(meeeyo.com)",
   "ExtractSpecificLines": "提取特定行(meeeyo.com)",
   "RemoveContentBetweenChars": "删除标签内的内容(meeeyo.com)",
   "ShuffleTextLines": "随机打乱(meeeyo.com)",
   "ConditionalTextOutput": "判断返回内容(meeeyo.com)",
   "TextConditionCheck": "文本按条件判断(meeeyo.com)",
   "TextConcatenation": "文本组合(meeeyo.com)",
   "ExtractSpecificData": "提取多层指定数据(meeeyo.com)",
   "FindFirstLineContent": "指定字符行参数(meeeyo.com)",

   #文件处理：meyo_node_File
   "FileListAndSuffix": "从路径加载(meeeyo.com)",
   "ReadExcelData": "读取表格数据(meeeyo.com)",
   "WriteExcelData": "写入表格数据(meeeyo.com)",
   "FindExcelData": "查找表格数据(meeeyo.com)",
   "ReadExcelRowOrColumnDiff": "读取表格数量差(meeeyo.com)",

}