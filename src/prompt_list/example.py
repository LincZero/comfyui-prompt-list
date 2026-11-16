from inspect import cleandoc
import torch

# 这是一个节点，将通过 `NODE_CLASS_MAPPINGS` 进行声明暴露
class Example:
    """
    示例节点: 图像反转

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

    CATEGORY = "Prompt List" # 分类
    RETURN_TYPES = ("IMAGE",) # 返回值类型
    #RETURN_NAMES = ("image_output_name",) 返回值名，默认名是 "返回值类型"
    DESCRIPTION = cleandoc(__doc__ or "") # 获取文档字符串充当节点描述，当鼠标悬浮在节点上时会显示这个
    FUNCTION = "test" # 执行的方法名 (自定义函数的名字，这里不是测试函数的意思)
    #OUTPUT_NODE = False # (默认是false) true则声明这个节点是工作流的终点，而不是中间处理节点
    #OUTPUT_TOOLTIPS = ("",) # 输出节点的工具提示

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        该节点: 这里有五个输入字段：
        - image。类型 Image
          tooltip 会在鼠标悬浮在输入上时弹出说明。
        - int_field。类型 INT
        - float_field。类型 FLOAT
        - print_to_screen。类型枚举
        - string_field。类型 STRING
        
        学习笔记: 类型有: 
        特殊: "INT"、"STRING"、"FLOAT"
        其他: "MODEL"、"VAE"、"CLIP"、"CONDITIONING"、"LATENT"、"IMAGE"
        输入类型  是节点上字段的特殊值。
        类型可以是一个列表，用于选择。
        """
        return {
            "required": {
                "image": ("IMAGE", {
                  "tooltip": "This is an image" # 鼠标悬浮注释
                }),
                "int_field": ("INT", {
                    "default": 0, # 默认值
                    "min": 0,     # 最小值
                    "max": 4096,  # 最大值
                    "step": 64,   # 滑块步长
                    "display": "number" # 仅外观：显示为 "number" 或 "slider"
                }),
                "float_field": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.01,
                    "round": 0.001, # 要舍入到的精度的值，默认为步长值。可以设置为 False 以禁用舍入
                    "display": "number"}),
                "print_to_screen": (["enable", "disable"],),
                "string_field": ("STRING", {
                    "multiline": False, # 如果你希望该字段看起来像 ClipTextEncode 节点上的字段，则为 True
                    "default": "Hello World!"
                }),
            },
        }

    # 功能: 反转图像
    # 参数:  self + 提前声明的5个参数
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
    如果任何输入发生变化，节点将始终重新执行，但此方法可用于强制节点在输入未变化时再次执行。
    做法:
    你可以让此节点返回一个数字或字符串。此值将与节点上次
    执行时返回的值进行比较，如果不同，则节点将再次执行。
    场景:
    此方法在核心仓库中用于 LoadImage 节点，它们将图像哈希作为字符串返回，
    如果图像哈希在多次执行之间发生变化，则 LoadImage 节点会再次执行。
    """
    #@classmethod
    #def IS_CHANGED(s, image, string_field, int_field, float_field, print_to_screen):
    #    return ""

class ImageSelector:
    """
    示例节点: 选择图像批次中最亮的那张
    """

    CATEGORY = "Prompt List"
    RETURN_TYPES = ("IMAGE",)
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "choose_image"

    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "images": ("IMAGE",), } }

    def choose_image(self, images):
        brightness = list(torch.mean(image.flatten()).item() for image in images)
        brightest = brightness.index(max(brightness))
        result = images[brightest].unsqueeze(0)
        return (result,)
