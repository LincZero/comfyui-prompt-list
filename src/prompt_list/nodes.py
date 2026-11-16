from .example import Example
from .example import ImageSelector

# 一个字典，包含要导出的所有节点及其名称
# 注意：名称应全局唯一
NODE_CLASS_MAPPINGS = {
    "Example": Example,
    "ImageSelector": ImageSelector,
}

# 一个字典，包含节点的友好/人类可读标题
NODE_DISPLAY_NAME_MAPPINGS = {
    "Example": "Example Node",
    "ImageSelector": "Image Selector",
}
