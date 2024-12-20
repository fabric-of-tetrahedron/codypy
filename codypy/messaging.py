import asyncio
import logging
from json import JSONDecodeError
from typing import Any, AsyncGenerator, Dict, Tuple

import pydantic_core as pd

from codypy.config import Configs

# 设置日志记录器
logger = logging.getLogger(__name__)
stream_logger = logging.getLogger(f"{__name__}.stream")

# 全局消息ID，用于标识每个JSON-RPC请求
MESSAGE_ID = 1


async def _send_jsonrpc_request(
    writer: asyncio.StreamWriter, method: str, params: Dict[str, Any] | None
) -> None:
    """
    向服务器发送JSON-RPC请求。

    参数:
        writer: 用于发送请求的asyncio StreamWriter。
        method: 要调用的JSON-RPC方法。
        params: 传递给JSON-RPC方法的参数，如果不需要参数则为None。

    异常:
        无
    """
    global MESSAGE_ID
    message: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": MESSAGE_ID,
        "method": method,
        "params": params,
    }

    # 将消息转换为JSON字符串
    json_message: bytes = pd.to_json(message)
    content_length: int = len(json_message)
    content_message: bytes = (
        f"Content-Length: {content_length}\r\n\r\n".encode() + json_message
    )

    # 向服务器发送JSON-RPC消息
    writer.write(content_message)
    await writer.drain()
    MESSAGE_ID += 1


async def _receive_jsonrpc_messages(reader: asyncio.StreamReader) -> str:
    """
    从提供的`asyncio.StreamReader`中读取JSON-RPC消息。

    参数:
        reader: 用于读取消息的`asyncio.StreamReader`。

    返回:
        JSON-RPC消息字符串。

    异常:
        asyncio.TimeoutError: 如果在5秒超时内无法读取消息。
    """
    headers: bytes = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=5.0)
    content_length: int = int(
        headers.decode("utf-8").split("Content-Length:")[1].strip()
    )

    json_data: bytes = await asyncio.wait_for(
        reader.readexactly(content_length), timeout=5.0
    )
    return json_data.decode("utf-8")


async def _handle_server_respones(
    reader: asyncio.StreamReader,
) -> AsyncGenerator[Dict[str, Any], Any]:
    """
    异步处理服务器响应，从提供的`asyncio.StreamReader`中读取JSON-RPC消息。

    此函数会产生每个JSON-RPC响应作为字典，直到发生超时。

    参数:
        reader: 用于读取JSON-RPC消息的`asyncio.StreamReader`。

    产生:
        表示JSON-RPC响应的字典。

    异常:
        asyncio.TimeoutError: 如果在5秒超时内无法读取JSON-RPC消息。
    """
    try:
        while True:
            response: str = await _receive_jsonrpc_messages(reader)
            yield pd.from_json(response)
    except asyncio.TimeoutError:
        yield pd.from_json("{}")


async def _has_method(json_response: Dict[str, Any]) -> bool:
    """
    检查提供的JSON响应是否包含"method"键。

    参数:
        json_response (Dict[str, Any]): 要检查的JSON响应。

    返回:
        bool: 如果JSON响应包含"method"键则返回True，否则返回False。
    """
    return "method" in json_response


async def _has_result(json_response: Dict[str, Any]) -> bool:
    """
    检查提供的JSON响应是否包含"result"键。

    参数:
        json_response (Dict[str, Any]): 要检查的JSON响应。

    返回:
        bool: 如果JSON响应包含"result"键则返回True，否则返回False。
    """
    return "result" in json_response


async def _extraxt_result(json_response: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    尝试从提供的JSON响应字典中提取"result"键的值。

    参数:
        json_response (Dict[str, Any]): 要提取"result"的JSON响应字典。

    返回:
        Dict[str, Any] | None: 如果存在"result"键，则返回其值，否则返回None。
    """
    try:
        return json_response["result"]
    except JSONDecodeError as _:
        return None


async def _extraxt_method(json_response) -> Dict[str, Any] | None:
    """
    尝试从提供的JSON响应字典中提取"method"键的值。

    参数:
        json_response (Dict[str, Any]): 要提取"method"的JSON响应字典。

    返回:
        Dict[str, Any] | None: 如果存在"method"键，则返回其值，否则返回None。
    """
    try:
        return json_response["method"]
    except JSONDecodeError as _:
        return None


# TODO: 移除未使用的函数
async def _handle_json_data(json_data, configs: Configs) -> Dict[str, Any] | None:
    """
    处理从远程源接收的JSON数据。

    参数:
        json_data (str): 要处理的JSON数据。
        configs (Configs): 处理过程中使用的配置设置。

    返回:
        Dict[str, Any] | None: 从JSON响应中提取的"method"或"result"，
        如果两者都不存在，则返回原始JSON响应。
    """
    json_response: Dict[str, Any] = pd.from_json(json_data)
    if await _has_method(json_response):
        logger.debug(
            "方法: %s, 参数: %s",
            json_response["method"],
            json_response.get("params"),
        )
        return await _extraxt_method(json_response)

    if await _has_result(json_response):
        result = await _extraxt_result(json_response)
        logger.debug("结果: %s", result)
        return result

    return json_response


async def _show_last_message(
    messages: Dict[str, Any],
    show_context_files: bool,
) -> Tuple[str, str, list[str]]:
    """
    检索消息记录中最后一条消息的发言者和文本。

    参数:
        messages (Dict[str, Any]): 包含消息历史的字典。

    返回:
        Tuple[str, str]: 包含最后一条消息的发言者和文本的元组。
    """
    if messages is not None and messages["type"] == "transcript":
        last_message = messages["messages"][-1:][0]
        logger.debug("最后一条消息: %s", last_message)
        speaker: str = last_message["speaker"]
        text: str = last_message["text"]

        context_file_results = []
        if show_context_files:
            context_files: list[any] = messages["messages"]

            for context_result in context_files:
                res = (
                    context_result["contextFiles"]
                    if "contextFiles" in context_result
                    else []
                )
                for reso in res:
                    uri = reso["uri"]["path"]
                    if "range" in reso:
                        rng = reso["range"]
                        rng_start = rng["start"]["line"]
                        rng_end = rng["end"]["line"]
                        context_file_results.append(f"{uri}:{rng_start}-{rng_end}")

        return speaker, text, context_file_results
    return ("", "", [])


async def _show_messages(message, configs: Configs) -> None:
    """
    打印消息记录中每条消息的发言者和文本。

    参数:
        message (dict): 包含消息历史的字典，其中"type"键设置为"transcript"，
                        "messages"键包含消息字典列表。
        configs (Configs): 处理过程中使用的配置设置。

    返回:
        无
    """
    if message["type"] == "transcript":
        for message in message["messages"]:
            logger.debug("%s: %s", message["speaker"], message["text"])


async def request_response(method_name: str, params, reader, writer) -> Any:
    """
    向服务器发送JSON-RPC请求并处理响应。

    参数:
        method_name (str): 要调用的JSON-RPC方法的名称。
        params: 传递给JSON-RPC方法的参数。
        reader (asyncio.StreamReader): 用于接收响应的读取器流。
        writer (asyncio.StreamWriter): 用于发送请求的写入器流。

    返回:
        Any: JSON-RPC请求的结果，如果没有可用结果则返回None。
    """
    logger.debug("发送命令: %s - %s", method_name, params)
    await _send_jsonrpc_request(writer, method_name, params)
    async for response in _handle_server_respones(reader):
        params = response.get("params", {})
        if not isinstance(params, dict):
            continue
        if params.get("isMessageInProgress"):
            stream_logger.debug("进行中的响应: %s", response)
        if response and await _has_result(response):
            logger.debug("响应: %s", response)
            return response["result"]

    return None
