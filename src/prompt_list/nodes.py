from .example import Example
from .example import ImageSelector

from .list import PromptList_CreateFromString
from .list import PromptList_Create
from .list import PromptList_Show
from .list import PromptList_GetItem
from .list import PromptList_SetItem
from .list import PromptList_JoinToString

# 一个字典，包含要导出的所有节点及其名称
# 注意：名称应全局唯一
NODE_CLASS_MAPPINGS = {
    "Example": Example,
    "Example ImageSelector": ImageSelector,

    "PromptList Create": PromptList_Create,
    "PromptList CreateFromString": PromptList_CreateFromString,
    "PromptList Show": PromptList_Show,
    "PromptList GetItem": PromptList_GetItem,
    "PromptList SetItem": PromptList_SetItem,
    "PromptList JoinToString": PromptList_JoinToString,
}

# 一个字典，包含节点的友好/人类可读标题
NODE_DISPLAY_NAME_MAPPINGS = {
    "Example": "Example Node",
    "Example ImageSelector": "Example Image Selector",
}
