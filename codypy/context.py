import logging
import os
from dataclasses import dataclass

# 创建一个日志记录器
logger = logging.getLogger(__name__)


@dataclass
class Uri:
    """
    表示统一资源标识符（URI）的数据类。

    属性:
        fsPath (str): 文件系统路径
        path (str): 通用路径
    """
    fsPath: str = ""
    path: str = ""


@dataclass
class Context:
    """
    表示上下文信息的数据类。

    属性:
        type (str): 上下文类型，默认为"file"
        uri (Uri | None): 与上下文相关的URI对象
    """
    type: str = "file"
    uri: Uri | None = None


# 存储上下文文件路径的列表
context_file_paths: list[Context] = []


def append_paths(*paths: str) -> list[Context]:
    """
    将提供的文件路径追加到 `context_file_paths` 列表中，为每个路径创建一个 `Context` 对象。

    参数:
        *paths (str): 一个或多个要追加到 `context_file_paths` 列表的文件路径。

    返回:
        list[Context]: 更新后的 `context_file_paths` 列表。

    功能:
        1. 遍历提供的所有路径
        2. 检查每个路径是否存在
        3. 为每个路径创建 Uri 和 Context 对象
        4. 将创建的 Context 对象添加到 context_file_paths 列表中
        5. 返回更新后的 context_file_paths 列表
    """
    for path in paths:
        # 检查路径是否存在
        if not os.path.exists(path):
            logger.warning("路径 %s 不存在", path)

        # 创建 Uri 对象
        uri = Uri()
        uri.fsPath = os.path.abspath(path).replace('\\', '/')
        uri.path = path

        # 创建 Context 对象
        context = Context()
        context.uri = uri

        # 将 Context 对象添加到列表中
        context_file_paths.append(context)

    return context_file_paths
