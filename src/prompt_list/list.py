"""
- "字符串列表" (主要指提示词字符串的列表) 的若干方法
  - 创建
  - 取值
  - 修改
  - 遍历
"""

from inspect import cleandoc
import json

class PromptList_CreateFromString:
    """将多行文本按行分割为提示词列表，忽略空行。"""

    CATEGORY = "Prompt List"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt_list",)
    OUTPUT_IS_LIST = (True,)          # 输出的是列表，而非单条字符串
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "function"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "",
                }),
            }
        }

    def function(self, text):
        lines = text.splitlines()
        result = [line.strip() for line in lines if line.strip()]
        return (result,)

class PromptList_Create:
    """通过动态数量的文本输入构造提示词列表。

    - text_1 可直接在节点上编辑
    - text_2 ~ text_N 为可选插槽，按需连线即可，未连接的会被自动跳过
    - 空白字符串（strip 后为空）不会加入列表
    """

    CATEGORY = "Prompt List"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt_list",)
    OUTPUT_IS_LIST = (True,)
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "function"

    # 可扩展的插槽数量上限，用户按需使用即可实现"动态数量"
    MAX_INPUTS = 20

    @classmethod
    def INPUT_TYPES(cls):
        optional = {}
        for i in range(2, cls.MAX_INPUTS + 1):
            optional[f"text_{i}"] = ("STRING", {
                "multiline": True,
                "forceInput": True,
            })
        return {
            "required": {
                "text_1": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "首个文本，可直接编辑；其余 text_2 ~ text_N 通过连线传入",
                }),
            },
            "optional": optional,
        }

    def function(self, text_1="", **kwargs):
        result = []
        if isinstance(text_1, str) and text_1.strip():
            result.append(text_1.strip())
        for i in range(2, self.MAX_INPUTS + 1):
            value = kwargs.get(f"text_{i}")
            if isinstance(value, str) and value.strip():
                result.append(value.strip())
        return (result,)

class PromptList_Show:
    """显示整个提示词列表（以换行拼接），同时可继续向下游传递列表。"""

    CATEGORY = "Prompt List"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt_list",)
    INPUT_IS_LIST = True              # 接收整个列表，而非逐项调用
    OUTPUT_IS_LIST = (True,)
    OUTPUT_NODE = True                # 作为输出节点，在 UI 中展示内容
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "function"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_list": ("STRING", {
                    "forceInput": True
                }),
            }
        }

    def function(self, prompt_list):
        # display_text = "\n".join(prompt_list) if isinstance(prompt_list, list) else str(prompt_list)
        if not isinstance(prompt_list, list):
            prompt_list = [prompt_list]
        # ensure_ascii=False 保证中文等非 ASCII 字符正常显示而非转义
        display_text = json.dumps(prompt_list, ensure_ascii=False, indent=2)
        return {
            "ui": {"text": [display_text]},
            "result": (prompt_list,),
        }


class PromptList_Modify:
    """根据索引修改列表中的某一项，输出修改后的新列表。"""

    CATEGORY = "Prompt List"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt_list",)
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (True,)
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "function"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_list": ("STRING", {"forceInput": True}),
                "index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999,
                    "step": 1,
                    "tooltip": "要修改的列表索引（从 0 开始）",
                }),
                "new_value": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "替换后的提示词内容",
                }),
            }
        }

    def function(self, prompt_list, index, new_value):
        index = index[0] if isinstance(index, list) else index
        new_value = new_value[0] if isinstance(new_value, list) else new_value

        if not isinstance(prompt_list, list):
            prompt_list = [prompt_list]

        # 下标溢出 / 非法时直接抛出异常，ComfyUI 报错终止执行
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError(f"index 必须为整数，收到: {type(index).__name__}")
        if index < 0 or index >= len(prompt_list):
            raise IndexError(
                f"索引 {index} 越界：列表长度为 {len(prompt_list)}，"
                f"有效范围为 [0, {len(prompt_list) - 1}]"
            )

        result = list(prompt_list)
        result[index] = new_value
        return (result,)


class PromptList_Iterate:
    """将列表遍历并拼接为一个字符串，可用分隔符控制格式。"""

    CATEGORY = "Prompt List"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("joined_text",)
    INPUT_IS_LIST = True
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "function"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_list": ("STRING", {"forceInput": True}),
                "separator": ("STRING", {
                    "default": ", ",
                    "multiline": False,
                    "tooltip": "拼接时使用的分隔符",
                }),
            }
        }

    def function(self, prompt_list, separator):
        separator = separator[0] if isinstance(separator, list) else separator
        if not isinstance(prompt_list, list):
            prompt_list = [prompt_list]
        return (separator.join(prompt_list),)
