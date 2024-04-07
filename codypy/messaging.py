import asyncio
from json import JSONDecodeError
from typing import Any, AsyncGenerator, Dict, Tuple

import pydantic_core as pd

from codypy.config import Configs

message_id = 1


async def _send_jsonrpc_request(
    writer: asyncio.StreamWriter, method: str, params: Dict[str, Any] | None
) -> None:
    """
    Sends a JSON-RPC request to the server.

    Args:
        writer: The asyncio StreamWriter to use for sending the request.
        method: The JSON-RPC method to call.
        params: The parameters to pass to the JSON-RPC method, or None if no parameters are required.

    Raises:
        None
    """
    global message_id
    message: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": message_id,
        "method": method,
        "params": params,
    }

    # Convert the message to JSON string
    json_message: str = pd.to_json(message).decode()
    content_length: int = len(json_message)
    content_message: str = f"Content-Length: {content_length}\r\n\r\n{json_message}"

    # Send the JSON-RPC message to the server
    writer.write(content_message.encode("utf-8"))
    await writer.drain()
    message_id += 1


async def _receive_jsonrpc_messages(reader: asyncio.StreamReader) -> str:
    """
    Reads a JSON-RPC message from the provided `asyncio.StreamReader`.

    Args:
        reader: The `asyncio.StreamReader` to read the message from.

    Returns:
        The JSON-RPC message as a string.

    Raises:
        asyncio.TimeoutError: If the message cannot be read within the 5 second timeout.
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
    Asynchronously handles server responses by reading JSON-RPC messages from the provided `asyncio.StreamReader`.

    This function yields each JSON-RPC response as a dictionary, until a timeout occurs.

    Args:
        reader: The `asyncio.StreamReader` to read the JSON-RPC messages from.

    Yields:
        A dictionary representing the JSON-RPC response.

    Raises:
        asyncio.TimeoutError: If a JSON-RPC message cannot be read within the 5 second timeout.
    """
    try:
        while True:
            response: str = await _receive_jsonrpc_messages(reader)
            yield pd.from_json(response)
    except asyncio.TimeoutError:
        yield pd.from_json("{}")


async def _hasMethod(json_response: Dict[str, Any]) -> bool:
    """
    Checks if the provided JSON response contains a "method" key.

    Args:
        json_response (Dict[str, Any]): The JSON response to check.

    Returns:
        bool: True if the JSON response contains a "method" key, False otherwise.
    """
    return "method" in json_response


async def _hasResult(json_response: Dict[str, Any]) -> bool:
    """
    Checks if the provided JSON response contains a "result" key.

    Args:
        json_response (Dict[str, Any]): The JSON response to check.

    Returns:
        bool: True if the JSON response contains a "result" key, False otherwise.
    """
    return "result" in json_response


async def _extraxtResult(json_response: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Attempts to extract the "result" key from the provided JSON response dictionary.

    Args:
        json_response (Dict[str, Any]): The JSON response dictionary to extract the "result" from.

    Returns:
        Dict[str, Any] | None: The value of the "result" key if it exists, otherwise None.
    """
    try:
        return json_response["result"]
    except JSONDecodeError as e:
        return None


async def _extraxtMethod(json_response) -> Dict[str, Any] | None:
    """
    Attempts to extract the "method" key from the provided JSON response dictionary.

    Args:
        json_response (Dict[str, Any]): The JSON response dictionary to extract the "method" from.

    Returns:
        Dict[str, Any] | None: The value of the "method" key if it exists, otherwise None.
    """
    try:
        return json_response["method"]
    except JSONDecodeError as e:
        return None


async def _handle_json_data(json_data, configs: Configs) -> Dict[str, Any] | None:
    """
    Handles the processing of JSON data received from a remote source.

    Args:
        json_data (str): The JSON data to be processed.
        configs (Configs): The configuration settings to use during processing.

    Returns:
        Dict[str, Any] | None: The extracted "method" or "result" from the JSON response, or the original JSON response if neither "method" nor "result" is present.
    """
    json_response: Dict[str, Any] = pd.from_json(json_data)
    if await _hasMethod(json_response):
        if configs.IS_DEBUGGING:
            print(f"Method: {json_response['method']}\n")
        if "params" in json_response and configs.IS_DEBUGGING:
            print(f"Params: \n{json_response['params']}\n")
        return await _extraxtMethod(json_response)

    if await _hasResult(json_response):
        if configs.IS_DEBUGGING:
            print(f"Result: \n\n{await _extraxtResult(json_response)}\n")
        return await _extraxtResult(json_response)

    return json_response


async def _show_last_message(
    messages: Dict[str, Any], is_debugging: bool
) -> Tuple[str, str]:
    """
    Retrieves the speaker and text of the last message in a transcript.

    Args:
        messages (Dict[str, Any]): A dictionary containing the message history.
        is_debugging (bool): A flag indicating whether debugging is enabled.

    Returns:
        Tuple[str, str]: A tuple containing the speaker and text of the last message.
    """
    if messages["type"] == "transcript":
        last_message = messages["messages"][-1:]
        if is_debugging:
            print(f"Last message: {last_message}")
        speaker: str = last_message[0]["speaker"]
        text: str = last_message[0]["text"]
        return speaker, text
    return ("", "")


async def _show_messages(message, configs: Configs) -> None:
    """
    Prints the speaker and text of each message in a transcript.

    Args:
        message (dict): A dictionary containing the message history, with a "type" key set to "transcript" and a "messages" key containing a list of message dictionaries.
        configs (Configs): The configuration settings to use during processing.

    Returns:
        None
    """
    if message["type"] == "transcript":
        for message in message["messages"]:
            if configs.IS_DEBUGGING:
                output = f"{message['speaker']}: {message['text']}\n"
                print(output)


async def request_response(
    method_name: str,
    params,
    debug_method_map,
    reader,
    writer,
    is_debugging: bool,
    callback=None,
) -> Any:
    """
    Sends a JSON-RPC request to a server and handles the response.

    Args:
        method_name (str): The name of the JSON-RPC method to call.
        params: The parameters to pass to the JSON-RPC method.
        debug_method_map (dict): A mapping of method names to a boolean indicating whether to print the response.
        reader (asyncio.StreamReader): The reader stream to use for receiving responses.
        writer (asyncio.StreamWriter): The writer stream to use for sending requests.
        is_debugging (bool): A flag indicating whether debugging is enabled.
        callback (Optional[Callable[[Any], Awaitable[Any]]]): An optional callback function to handle the response result.

    Returns:
        Any: The result of the JSON-RPC request, or None if no result is available.
    """
    await _send_jsonrpc_request(writer, method_name, params)
    async for response in _handle_server_respones(reader):

        if is_debugging and await _hasMethod(response):
            method_name = response["method"]
            if method_name in debug_method_map and debug_method_map[method_name]:
                print(f"Response: \n\n{response}\n")
            if method_name not in debug_method_map:
                print(f"Response: \n\n{response}\n")

        if response and await _hasResult(response):
            if is_debugging:
                print(f"Result: \n\n{response}\n")
            if callback:
                return await callback(response["result"])
            else:
                return response["result"]

    return None