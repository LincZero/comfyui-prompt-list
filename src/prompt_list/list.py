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


class PromptList_CreateFromUpstream(io.ComfyNode):
    """从上游连线收集文本创建整张提示词列表：每个连上的输入对应一项。

    输入框的规则和内置的 “Create List” 节点一致：连上最后一个输入就会多出一个，
    断开后自动收回；这里只是把输出换成 python 列表（STRING_PYLIST）。
    空字符串也保留为空项，不跳过。
    """

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="PromptList CreateFromUpstream",
            display_name="PromptList Create From Upstream (Auto)",
            category="Prompt List",
            description=cleandoc(__doc__ or ""),
            search_aliases=["autogrow", "grow inputs", "collect strings", "from upstream",
                            "连线", "上游", "自动增加", "端口", "收集"],
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
        # 空字符串也保留为空项
        return io.NodeOutput([(value or "").strip() for value in texts.values()])


# [warning] PromptList_CreateFromStrings 节点的动态输入比较复杂，部分 vibe coding 的代码我也没弄懂
class PromptList_CreateFromStrings:
    """从多个单行文本输入创建或整体修改整张提示词列表：每个输入框对应一项（下标从 0 开始）。"""

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

    ITEM = "{{item}}"
    MULTILINE = False
    # 几个 create 节点共用的模板说明，避免每个节点的描述里重复写一遍
    TEMPLATE_HELP = f"""\
    接了 prompt_list 时，每个框/每行就是对应项的模板：`{ITEM}` 代表该项原来的内容，也是默认值（等于不改）。
    写成 `{ITEM}, 新内容` 是追加到末尾、`新内容, {ITEM}` 是插到开头；不含 `{ITEM}` 时直接覆盖该项，留空则清空该项。
    比列表多出来的非空框/行会追加成新项；列表比框/行多时，多出来的项原样保留。
    不接 prompt_list 时就是纯创建：每个框/每行一项，空值就是空字符串。"""
    # 给“添加节点”搜索用：这些节点既能创建也能整体修改列表
    SEARCH_ALIASES = ["create prompt list", "set items", "modify list", "batch edit", "replace items",
                      "创建", "批量", "修改", "替换", "提示词列表"]
    CATEGORY = "Prompt List"
    RETURN_TYPES = ("STRING_PYLIST",)
    RETURN_NAMES = ("prompt_list",)
    DESCRIPTION = cleandoc(f"{__doc__ or ''}\n\n{TEMPLATE_HELP}")
    FUNCTION = "function"

    @classmethod
    def INPUT_TYPES(cls):
        # inputcount 决定界面上的文本输入框数量，前端的 “Update Inputs” 按钮负责增删。
        # 这里只声明 text_0 / text_1，让节点默认可用；其余 text_N 由前端按 inputcount
        # 动态添加，Python 端靠 FlexibleOptionalInputType 接收这些未声明的输入。
        # 输入框下标从 0 开始，和 GetItem / SetItem 的 index 直接对应。
        text_options = {"multiline": cls.MULTILINE, "default": cls.ITEM}
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
            # prompt_list 可选：不接就是纯创建，接了就是批量修改
            "optional": cls.FlexibleOptionalInputType("STRING", {
                "prompt_list": ("STRING_PYLIST", {"forceInput": True}),
                "text_0": ("STRING", dict(text_options)),
                "text_1": ("STRING", dict(text_options)),
            }),
        }

    def function(self, inputcount, prompt_list=None, **kwargs):
        # 每个输入框对应一项（下标从 0 开始）
        templates = [(kwargs.get(f"text_{index}") or "").strip() for index in range(inputcount)]
        return (self._merge(templates, prompt_list),)

    def _merge(self, templates, prompt_list):
        """把一组模板字符串套到 prompt_list 上；prompt_list 为空时每个模板直接生成一项。"""
        if prompt_list is not None and not isinstance(prompt_list, (list, tuple)):
            raise TypeError(f"prompt_list 必须为列表，收到: {type(prompt_list).__name__}")

        # 没有上游列表：每个模板就是一项（空模板就是空字符串）
        if not prompt_list:
            return [text.replace(self.ITEM, "") for text in templates]

        # 第 index 个模板改第 index 项。列表更长时，后面的项不参与处理、原样保留
        result = list(prompt_list)
        for index, text in enumerate(templates):
            if index < len(result):
                result[index] = text.replace(self.ITEM, result[index])
            else:
                # 列表更短：多出来的模板作为新项追加（空的就不追加，避免凭空多出空项）
                value = text.replace(self.ITEM, "")
                if value.strip():
                    result.append(value)
        return result


class PromptList_CreateFromStringsMulti(PromptList_CreateFromStrings):
    """从多个多行文本输入创建或整体修改整张提示词列表：每个输入框对应一项（可以写多行）。"""

    MULTILINE = True
    SEARCH_ALIASES = [*PromptList_CreateFromStrings.SEARCH_ALIASES, "multiline", "multi line", "多行"]
    DESCRIPTION = cleandoc(f"{__doc__ or ''}\n\n{PromptList_CreateFromStrings.TEMPLATE_HELP}")


class PromptList_CreateFromString(PromptList_CreateFromStrings):
    """将多行文本按行分割为提示词列表：一行一项，也可以接上游列表做整体修改。"""

    SEARCH_ALIASES = ["split lines", "text to list", "lines to list", "from string",
                      "按行", "分行", "拆行", "多行文本转列表", "修改", "替换"]
    DESCRIPTION = cleandoc(f"{__doc__ or ''}\n\n{PromptList_CreateFromStrings.TEMPLATE_HELP}")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "",
                }),
            },
            "optional": {
                "prompt_list": ("STRING_PYLIST", {"forceInput": True}),
            },
        }

    def function(self, text, prompt_list=None):
        if not isinstance(text, str):
            raise TypeError(f"text 必须为字符串，收到: {type(text).__name__}")

        # 空行也保留为空字符串，保证行号和列表下标一一对应
        return (self._merge([line.strip() for line in text.splitlines()], prompt_list),)


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
