from .example import Example
from .example import ImageSelector

from .list import PromptList_CreateFromString
from .list import PromptList_Create
from .list import PromptList_Show
from .list import PromptList_Modify
from .list import PromptList_Iterate

# 一个字典，包含要导出的所有节点及其名称
# 注意：名称应全局唯一
NODE_CLASS_MAPPINGS = {
    "Example": Example,
    "ImageSelector": ImageSelector,

    "PromptList Creat": PromptList_Create,
    "PromptList Creat": PromptList_CreateFromString,
    "PromptList Show": PromptList_Show,
    "PromptList Modify": PromptList_Modify,
    "PromptList Iterate": PromptList_Iterate,
}

# 一个字典，包含节点的友好/人类可读标题
NODE_DISPLAY_NAME_MAPPINGS = {
    "Example": "Example Node",
    "ImageSelector": "Image Selector",
}
