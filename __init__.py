"""Top-level package for promptlist."""

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]

__author__ = """PromptList"""
__email__ = "762699299@qq.com"
__version__ = "0.0.1"

from .src.promptlist.nodes import NODE_CLASS_MAPPINGS
from .src.promptlist.nodes import NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./web"
