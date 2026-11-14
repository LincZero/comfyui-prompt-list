from inspect import cleandoc
class Example:
    """
    一个示例节点

    类方法
    -------------
    INPUT_TYPES (dict)：
        告诉主程序节点的输入参数。
    IS_CHANGED：
        可选方法，用于控制节点何时重新执行。

    属性
    ----------
    RETURN_TYPES (`tuple`)：
        输出元组中每个元素的类型。
    RETURN_NAMES (`tuple`)：
        可选：输出元组中每个输出的名称。
    FUNCTION (`str`)：
        入口点方法的名称。例如，如果 `FUNCTION = "execute"`，则将运行 Example().execute()
    OUTPUT_NODE ([`bool`])：
        如果此节点是输出节点，从图中输出结果/图像。SaveImage 节点就是一个例子。
        后端会遍历这些输出节点，并且如果它们的父图正确连接，则尝试执行它们的所有父节点。
        如果不存在，则假定为 False。
    CATEGORY (`str`)：
        节点应在 UI 中出现的类别。
    execute(s) -> tuple || None：
        入口点方法。此方法的名称必须与属性 `FUNCTION` 的值相同。
        例如，如果 `FUNCTION = "execute"`，则此方法名必须为 `execute`；如果 `FUNCTION = "foo"`，则必须为 `foo`。
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
            返回一个字典，其中包含所有输入字段的配置。
            一些类型（字符串）："MODEL"、"VAE"、"CLIP"、"CONDITIONING"、"LATENT"、"IMAGE"、"INT"、"STRING"、"FLOAT"。
            输入类型 "INT"、"STRING" 或 "FLOAT" 是节点上字段的特殊值。
            类型可以是一个列表，用于选择。

            返回：`dict`：
                - 键 input_fields_group（`string`）：可以是 required、hidden 或 optional。节点类必须具有属性 `required`
                - 值 input_fields（`dict`）：包含输入字段配置：
                    * 键 field_name（`string`）：入口点方法的参数名称
                    * 值 field_config（`tuple`）：
                        + 第一个值是一个字符串，表示字段类型，或用于选择的列表。
                        + 第二个值是类型 "INT"、"STRING" 或 "FLOAT" 的配置。
        """
        return {
            "required": {
                "image": ("Image", { "tooltip": "This is an image"}),
                "int_field": ("INT", {
                    "default": 0,
                    "min": 0, # 最小值
                    "max": 4096, # 最大值
                    "step": 64, # 滑块步长
                    "display": "number" # 仅外观：显示为 "number" 或 "slider"
                }),
                "float_field": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "round": 0.001, # 表示要舍入到的精度的值，默认将设置为步长值。可以设置为 False 以禁用舍入。
                    "display": "number"}),
                "print_to_screen": (["enable", "disable"],),
                "string_field": ("STRING", {
                    "multiline": False, # 如果你希望该字段看起来像 ClipTextEncode 节点上的字段，则为 True
                    "default": "Hello World!"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    #RETURN_NAMES = ("image_output_name",)
    DESCRIPTION = cleandoc(__doc__)
    FUNCTION = "test"

    #OUTPUT_NODE = False
    #OUTPUT_TOOLTIPS = ("",) # 输出节点的工具提示

    CATEGORY = "Example"

    def test(self, image, string_field, int_field, float_field, print_to_screen):
        if print_to_screen == "enable":
            print(f"""Your input contains:
                string_field aka input text: {string_field}
                int_field: {int_field}
                float_field: {float_field}
            """)
        #对图像做一些处理，在这个例子中我只是将其反转
        image = 1.0 - image
        return (image,)

    """
        如果任何输入发生变化，节点将始终重新执行，但
        此方法可用于强制节点在输入未变化时再次执行。
        你可以让此节点返回一个数字或字符串。此值将与节点上次
        执行时返回的值进行比较，如果不同，则节点将再次执行。
        此方法在核心仓库中用于 LoadImage 节点，它们将图像哈希作为字符串返回，如果图像哈希
        在多次执行之间发生变化，则 LoadImage 节点会再次执行。
    """
    #@classmethod
    #def IS_CHANGED(s, image, string_field, int_field, float_field, print_to_screen):
    #    return ""


# 一个字典，包含要导出的所有节点及其名称
# 注意：名称应全局唯一
NODE_CLASS_MAPPINGS = {
    "Example": Example
}

# 一个字典，包含节点的友好/人类可读标题
NODE_DISPLAY_NAME_MAPPINGS = {
    "Example": "Example Node"
}

class ImageSelector:
    CATEGORY = "example"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "images": ("IMAGE",), } }
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "choose_image"
