from .example import Example
from .example import ImageSelector

from .list import PromptList_CreateFromString
from .list import PromptList_CreateFromStrings
from .list import PromptList_CreateFromStringsMulti
from .list import PromptList_CreateFromUpstream
from .list import PromptList_CreateFromLists
from .list import PromptList_Show
from .list import PromptList_GetItem
from .list import PromptList_SetItem
from .list import PromptList_JoinToString

# 一个字典，包含要导出的所有节点及其名称
# 注意：名称应全局唯一
NODE_CLASS_MAPPINGS = {
    # "Example": Example,
    # "Example ImageSelector": ImageSelector,

    "PromptList CreateFromString": PromptList_CreateFromString,
    "PromptList CreateFromStrings": PromptList_CreateFromStrings,
    "PromptList CreateFromStringsMulti": PromptList_CreateFromStringsMulti,
    "PromptList CreateFromUpstream": PromptList_CreateFromUpstream,
    "PromptList CreateFromLists": PromptList_CreateFromLists,
    "PromptList Show": PromptList_Show,
    "PromptList GetItem": PromptList_GetItem,
    "PromptList SetItem": PromptList_SetItem,
    "PromptList JoinToString": PromptList_JoinToString,
}

# 一个字典，包含节点的友好/人类可读标题
NODE_DISPLAY_NAME_MAPPINGS = {
    # "Example": "Example Node",
    # "Example ImageSelector": "Example Image Selector",

    "PromptList CreateFromString": "PromptList Create From String",
    "PromptList CreateFromStrings": "PromptList Create From Strings",
    "PromptList CreateFromStringsMulti": "PromptList Create From Strings (Multi)",
    "PromptList CreateFromUpstream": "PromptList Create From Upstream (Auto)",
    "PromptList CreateFromLists": "PromptList Create From Lists (Concat)",
}
