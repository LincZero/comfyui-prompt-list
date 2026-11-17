"""
- "字符串列表" (主要指提示词字符串的列表) 的若干方法
  - 创建
  - 取值
  - 修改
  - 遍历

注意：这里的列表是 python 列表，而非 ComfyUI 列表。不是顺序任务序列，而是单个数据。
"""

from inspect import cleandoc
import json


class PromptList_CreateFromString:
    """将多行文本按行分割为提示词列表，忽略空行。"""

    CATEGORY = "Prompt List"
    RETURN_TYPES = ("STRING_PYLIST",)
    RETURN_NAMES = ("prompt_list",)
    #INPUT_IS_LIST = False
    #OUTPUT_IS_LIST = (False,)
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
        if not isinstance(text, str):
            raise TypeError(f"text 必须为字符串，收到: {type(text).__name__}")

        result = [line.strip() for line in text.splitlines() if line.strip()]
        return (result,)


class PromptList_Create:
    """从动态数量的文本输入创建整张提示词列表：每项一个，空白项忽略。"""

    CATEGORY = "Prompt List"
    RETURN_TYPES = ("STRING_PYLIST",)
    RETURN_NAMES = ("prompt_list",)
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "function"

    @classmethod
    def INPUT_TYPES(cls):
        # 基础输入：控制动态文本输入的数量
        base_inputs = {
            "required": {
                "inputcount": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 100, # 可根据需要调整上限
                    "step": 1,
                    "tooltip": "设置文本输入项的数量。调整后点击“Update Inputs”按钮刷新端口。",
                }),
            }
        }

        # 动态生成 text_1, text_2, ... 等输入
        # 这里默认生成 2 个，前端按钮会通过 JavaScript 重新触发 INPUT_TYPES
        dynamic_inputs = {}
        for i in range(1, 3): 
            key = f"text_{i}"
            dynamic_inputs[key] = ("STRING", {
                "multiline": True,
                "default": "",
                "tooltip": f"第 {i} 项提示词内容",
            })

        # 合并输入
        base_inputs["required"].update(dynamic_inputs)
        return base_inputs

    def function(self, inputcount, **kwargs):
        # 收集所有非空的文本输入
        # 根据键名 text_1, text_2... 排序以确保顺序与界面一致
        sorted_keys = sorted(
            [k for k in kwargs if k.startswith("text_")], 
            key=lambda x: int(x.split("_")[1])
        )

        result = []
        for key in sorted_keys:
            value = kwargs.get(key, "").strip()
            if value: # 忽略空白项
                result.append(value)
                
        # 如果希望强制返回 inputcount 数量的项（即使有些为空），可以改用下面的逻辑：
        # result = [kwargs.get(f"text_{i}", "").strip() for i in range(1, inputcount + 1)]
        
        return (result,)


class PromptList_Show:
    """以 JSON 形式（自动换行缩进）显示整张列表；同时把整张列表原样透传给下游。"""

    CATEGORY = "Prompt List"
    RETURN_TYPES = ("STRING_PYLIST",)
    RETURN_NAMES = ("prompt_list",)
    OUTPUT_NODE = True                  # 作为输出节点，在 UI 上渲染结果
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "function"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_list": ("STRING_PYLIST",),
            }
        }

    def function(self, prompt_list):
        if not isinstance(prompt_list, (list, tuple)):
            raise TypeError(f"prompt_list 必须为列表，收到: {type(prompt_list).__name__}")
        # ensure_ascii=False 让中文原样输出；indent=2 自动换行并缩进。
        display_text = json.dumps(list(prompt_list), ensure_ascii=False, indent=2)
        return {
            "ui": {"text": [display_text]},
            "result": (list(prompt_list),),
        }


class PromptList_GetItem:
    """根据索引获取列表中的某一项。"""

    CATEGORY = "Prompt List"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    #INPUT_IS_LIST = False
    #OUTPUT_IS_LIST = (False,)
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "function"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_list": ("STRING_PYLIST", {"forceInput": True}),
                "index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 9999,
                    "step": 1,
                    "tooltip": "要获取的列表索引（从 0 开始）",
                }),
            }
        }

    def function(self, prompt_list, index):
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError(f"index 必须为整数，收到: {type(index).__name__}")
        if not isinstance(prompt_list, (list, tuple)):
            raise TypeError(f"prompt_list 必须为列表，收到: {type(prompt_list).__name__}")
        if index < 0 or index >= len(prompt_list):
            raise IndexError(
                f"索引 {index} 越界：列表长度为 {len(prompt_list)}，"
                f"有效范围为 [0, {len(prompt_list) - 1}]"
            )

        result = list(prompt_list)
        return (result[index],)


class PromptList_SetItem:
    """根据索引修改列表中的某一项，输出修改后的新列表。"""

    CATEGORY = "Prompt List"
    RETURN_TYPES = ("STRING_PYLIST",)
    RETURN_NAMES = ("prompt_list",)
    #INPUT_IS_LIST = False
    #OUTPUT_IS_LIST = (False,)
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "function"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_list": ("STRING_PYLIST", {"forceInput": True}),
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
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError(f"index 必须为整数，收到: {type(index).__name__}")
        if not isinstance(prompt_list, (list, tuple)):
            raise TypeError(f"prompt_list 必须为列表，收到: {type(prompt_list).__name__}")
        if index < 0 or index >= len(prompt_list):
            raise IndexError(
                f"索引 {index} 越界：列表长度为 {len(prompt_list)}，"
                f"有效范围为 [0, {len(prompt_list) - 1}]"
            )

        result = list(prompt_list)
        result[index] = new_value
        return (result,)


class PromptList_JoinToString:
    """将列表遍历并拼接为一个字符串，可用分隔符控制格式。"""

    CATEGORY = "Prompt List"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("joined_text",)
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "function"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_list": ("STRING_PYLIST", {"forceInput": True}),
                "separator": ("STRING", {
                    "default": ", ",
                    "multiline": False,
                    "tooltip": "拼接时使用的分隔符",
                }),
            }
        }

    def function(self, prompt_list, separator):
        if not isinstance(separator, str):
            raise TypeError(f"separator 必须为字符串，收到: {type(separator).__name__}")
        if not isinstance(prompt_list, (list, tuple)):
            raise TypeError(f"prompt_list 必须为列表，收到: {type(prompt_list).__name__}")
        # 若元素含非 str，join 会自然抛 TypeError，语义清晰。
        return (separator.join(prompt_list),)
