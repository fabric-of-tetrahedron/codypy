import os
import platform
from typing import Any

import aiofiles
import aiohttp

from codypy.config import Configs
from codypy.messaging import request_response


async def _get_platform_arch() -> str | None:
    """
    识别当前系统的操作系统和架构。

    返回：
        str | None: 表示平台和架构的字符串，如果无法确定平台/架构则返回None。
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    # 根据系统和机器类型返回对应的平台架构
    if system == "linux":
        if machine == "x86_64":
            return "linux_x64"
        elif machine == "aarch64":
            return "linux_arm64"
    elif system == "darwin":
        if machine == "x86_64":
            return "macos_x64"
        elif machine == "arm64":
            return "macos_arm64"
    elif system == "windows":
        if machine == "x64":
            return "win_x64"

    return None


async def _format_arch(arch: str) -> str:
    """
    将平台架构字符串格式化为更易读的格式。

    参数：
        arch (str): 要格式化的平台架构字符串。

    返回：
        str: 格式化后的平台架构字符串。
    """
    # 将内部使用的架构标识转换为更易读的格式
    if arch == "linux_x64":
        return "linux-x64"
    if arch == "linux_arm64":
        return "linux-arm64"
    if arch == "macos_x64":
        return "macos-x64"
    if arch == "macos_arm64":
        return "macos-arm64"
    if arch == "win_x64":
        return "win-x64"


async def _has_file(binary_path: str, cody_agent_bin: str) -> bool:
    """
    检查指定二进制路径和文件名是否存在文件。

    参数：
        binary_path (str): 包含文件的目录路径。
        cody_agent_bin (str): 要检查的文件名。

    返回：
        bool: 如果文件存在则返回True，否则返回False。
    """
    joined_path_and_file = os.path.join(binary_path, cody_agent_bin)
    return os.path.isfile(joined_path_and_file)


async def _check_for_binary_file(
    binary_path: str, cody_name: str, version: str
) -> bool:
    """
    检查指定路径是否存在Cody代理的二进制文件。

    参数：
        binary_path (str): 包含Cody代理二进制文件的目录路径。
        cody_name (str): Cody代理的名称。
        version (str): Cody代理的版本。

    返回：
        bool: 如果Cody代理二进制文件存在则返回True，否则返回False。
    """
    cody_agent = await _format_binary_name(cody_name, version)
    return await _has_file(binary_path, cody_agent)


async def _format_binary_name(cody_name: str, version: str) -> str:
    """
    格式化Cody代理二进制文件的名称。

    参数：
        cody_name (str): Cody代理的名称。
        version (str): Cody代理的版本。

    返回：
        str: 格式化后的Cody代理二进制文件名称。
    """
    arch = await _get_platform_arch()
    formatted_arch = await _format_arch(arch)
    return (
        f"{cody_name}-{formatted_arch}-{version}{'.exe' if arch == 'win-x64' else ''}"
    )


async def _download_binary_to_path(
    binary_path: str, cody_name: str, version: str
) -> bool:
    """
    从GitHub发布页下载二进制文件到指定路径。

    参数：
        binary_path (str): 二进制文件应下载到的目录路径。
        cody_name (str): 要下载的二进制文件名称。
        version (str): 要下载的二进制文件版本。

    返回：
        bool: 下载成功返回True，失败返回False。
    """
    cody_agent = await _format_binary_name(cody_name, version)
    cody_binaray_path = os.path.join(binary_path, cody_agent)

    download_url = f"https://github.com/sourcegraph/cody/releases/download/agent-v{version}/{cody_agent}"
    print(f"Debug: Downloading from URL: {download_url}")

    async with aiohttp.ClientSession() as session:
        async with session.get(download_url) as response:
            if response.status != 200:
                print(f"HTTP错误: {response.status}")
                return False

            try:
                async with aiofiles.open(cody_binaray_path, "wb") as f:
                    content = await response.read()
                    await f.write(content)
                    print(f"已下载 {cody_agent} 到 {binary_path}")

                    # 为下载的文件设置执行权限 (chmod +x)
                    os.chmod(cody_binaray_path, 0o755)
                    return True
            except Exception as err:
                print(f"写入文件时发生错误: {err}")
                return False


async def get_remote_repositories(
    reader,
    writer,
    id: str,
    configs: Configs,
) -> Any:
    """
    获取远程仓库信息。

    参数：
        reader: 读取器对象。
        writer: 写入器对象。
        id (str): 请求标识符。
        configs (Configs): 配置对象。

    返回：
        Any: 远程仓库信息。
    """
    return await request_response("chat/remoteRepos", id, reader, writer, configs)


async def receive_webviewmessage(reader, writer, params, configs: Configs) -> Any:
    """
    接收Webview消息。

    参数：
        reader: 读取器对象。
        writer: 写入器对象。
        params: 消息参数。
        configs (Configs): 配置对象。

    返回：
        Any: Webview消息处理结果。
    """
    return await request_response(
        "webview/receiveMessage",
        params,
        reader,
        writer,
        configs,
    )
