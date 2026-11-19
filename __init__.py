"""Top-level package for prompt_list."""

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]

__author__ = """Prompt List"""
__email__ = "762699299@qq.com"
__version__ = "0.0.2"

from .src.prompt_list.nodes import NODE_CLASS_MAPPINGS
from .src.prompt_list.nodes import NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./web"
