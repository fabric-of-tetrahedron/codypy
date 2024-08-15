# 导入 dataclasses 模块中的 dataclass 装饰器
from dataclasses import dataclass

# 定义 ANSI 转义序列，用于重置终端颜色
RESET = "\033[0m"

# 定义前景色的 ANSI 转义序列
BLACK = "\033[30m"    # 黑色
RED = "\033[31m"      # 红色
GREEN = "\033[32m"    # 绿色
YELLOW = "\033[33m"   # 黄色
BLUE = "\033[34m"     # 蓝色
MAGENTA = "\033[35m"  # 洋红色
CYAN = "\033[36m"     # 青色
WHITE = "\033[37m"    # 白色


@dataclass
class Configs:
    """
    配置类，用于存储应用程序的各种设置。

    属性:
        BINARY_PATH (str): 二进制文件的路径，默认为空字符串。
        SERVER_ADDRESS (tuple): 服务器地址，包含主机名和端口号，默认为 ("localhost", 3113)。
        WORKSPACE (str): 工作空间路径，默认为空字符串。
        USE_TCP (bool): 是否使用 TCP 连接，默认为 False。
        IS_DEBUGGING (bool): 是否处于调试模式，默认为 False。
    """
    BINARY_PATH: str = ""
    SERVER_ADDRESS = ("localhost", 3113)
    WORKSPACE: str = ""
    USE_TCP: bool = False
    IS_DEBUGGING: bool = False


# 创建全局配置对象
configs = Configs()


async def get_configs() -> Configs:
    """
    获取全局配置对象。

    这个异步函数返回全局的配置对象，可以用于在应用程序的不同部分访问配置信息。

    返回:
        Configs: 全局配置对象。

    示例:
        async def some_function():
            config = await get_configs()
            print(config.WORKSPACE)
    """
    return configs
