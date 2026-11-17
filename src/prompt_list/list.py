"""
- "字符串列表" (主要指提示词字符串的列表) 的若干方法
  - 创建
  - 取值
  - 修改
  - 遍历

注意：这里的列表是 python 列表，而非 ComfyUI 列表。不是顺序任务序列，而是单个数据。
"""

from inspect import cleandoc
from comfy_api.latest import io
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


class PromptList_CreateAuto(io.ComfyNode):
    """从自动增殖的文本输入创建整张提示词列表：每项一个，空白项忽略。

    输入框的规则和内置的 “Create List” 节点一致：连上最后一个输入就会多出一个，
    断开后自动收回；这里只是把输出换成 python 列表（STRING_PYLIST）。
    """

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="PromptList CreateAuto",
            display_name="PromptList Create (Auto)",
            category="Prompt List",
            description=cleandoc(__doc__ or ""),
            inputs=[
                io.Autogrow.Input(
                    "texts",
                    template=io.Autogrow.TemplatePrefix(
                        input=io.String.Input("text", multiline=True, default=""),
                        prefix="text",
                        min=1,
                        max=100,
                    ),
                ),
            ],
            outputs=[io.Custom("STRING_PYLIST").Output(display_name="prompt_list")],
        )

    @classmethod
    def execute(cls, texts: io.Autogrow.Type) -> io.NodeOutput:
        result = []
        for value in texts.values():
            text = (value or "").strip()
            if text:
                result.append(text)
        return io.NodeOutput(result)


# [warning] PromptList_Create 节点的动态输入比较复杂，部分 vibe coding 的代码我也没弄懂
class PromptList_Create:
    """从动态数量的文本输入创建整张提示词列表：每项一个，空白项忽略。"""

    class FlexibleOptionalInputType(dict):
        """让 INPUT_TYPES 接受任意名字的输入。

        ComfyUI 判断输入是否合法时用的是 `name in INPUT_TYPES()["optional"]`，
        所以这里对未声明的 key 一律返回 True，并给出统一的类型；已声明的 key
        仍然返回原本的定义。
        """

        def __init__(self, type, data=None):
            super().__init__(data or {})
            self.type = type

        def __contains__(self, key):
            return True

        def __getitem__(self, key):
            if super().__contains__(key):
                return super().__getitem__(key)
            return (self.type,)

    CATEGORY = "Prompt List"
    RETURN_TYPES = ("STRING_PYLIST",)
    RETURN_NAMES = ("prompt_list",)
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "function"

    @classmethod
    def INPUT_TYPES(cls):
        # inputcount 决定界面上的文本输入框数量，前端的 “Update Inputs” 按钮负责增删。
        # 这里只声明 text_1 / text_2，让节点默认可用；其余 text_N 由前端按 inputcount
        # 动态添加，Python 端靠 FlexibleOptionalInputType 接收这些未声明的输入。
        return {
            "required": {
                "inputcount": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 100,  # 与 web/prompt_list.js 里的 MAX_TEXT_INPUTS 保持一致
                    "step": 1,
                    "tooltip": "设置文本输入项的数量。调整后点击“Update Inputs”按钮刷新端口。",
                }),
            },
            "optional": cls.FlexibleOptionalInputType("STRING", {
                "text_1": ("STRING", {"multiline": True, "default": ""}),
                "text_2": ("STRING", {"multiline": True, "default": ""}),
            }),
        }

    def function(self, inputcount, **kwargs):
        # 只读取 inputcount 范围内的输入，空白项忽略。
        result = []
        for index in range(1, inputcount + 1):
            text = (kwargs.get(f"text_{index}") or "").strip()
            if text:
                result.append(text)
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
