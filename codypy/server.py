import asyncio
import datetime
import logging
import os
from asyncio.subprocess import Process

from codypy.exceptions import (
    AgentBinaryNotFoundError,
    ServerTCPConnectionError,
)
from codypy.messaging import _send_jsonrpc_request

# 设置日志记录器
logger = logging.getLogger(__name__)


class CodyServer:
    """
    Cody服务器类，用于管理与Cody代理的连接和通信。
    """

    @classmethod
    async def init(
            cls,
            cody_binary_file: str,
            version: str,
            use_tcp: bool = False,  # 默认使用stdio，因为ca-certificate验证的原因
    ) -> "CodyServer":
        """
        初始化CodyServer实例的类方法。

        参数:
        binary_path (str): 二进制文件的路径
        version (str): Cody代理的版本
        use_tcp (bool): 是否使用TCP连接，默认为False

        返回:
        CodyServer: 初始化后的CodyServer实例
        """
        # cody_binary = await _get_cody_binary(binary_path, version)
        cody_server = cls(cody_binary_file, use_tcp)
        await cody_server._create_server_connection()
        return cody_server

    def __init__(self, cody_binary: str, use_tcp: bool) -> None:
        """
        初始化CodyServer实例。

        参数:
        cody_binary (str): Cody代理二进制文件的路径
        use_tcp (bool): 是否使用TCP连接
        """
        self.cody_binary = cody_binary
        self.use_tcp = use_tcp
        self._process: Process | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def _create_server_connection(
            self, test_against_node_source: bool = False
    ) -> None:
        """
        异步创建与Cody服务器的连接。

        如果`cody_binary`为空字符串，则抛出异常。
        根据`use_tcp`和调试标志设置环境变量。
        创建子进程运行Cody代理，可以是执行二进制文件或运行指定的index.js文件。
        根据`use_tcp`标志，使用stdio或TCP连接到代理。
        如果TCP连接失败（重试5次后），抛出异常。

        参数:
        test_against_node_source (bool): 是否使用Node源代码进行测试，默认为False

        异常:
        AgentBinaryNotFoundError: 如果Cody代理二进制文件路径为空
        ServerTCPConnectionError: 如果TCP连接失败
        """
        if not test_against_node_source and self.cody_binary == "":
            raise AgentBinaryNotFoundError(
                "Cody代理二进制文件路径为空。您需要指定BINARY_PATH为代理二进制文件"
                "或index.js文件的绝对路径。"
            )

        # 设置调试相关的环境变量
        debug = logger.getEffectiveLevel() == logging.DEBUG
        os.environ["CODY_AGENT_DEBUG_REMOTE"] = str(self.use_tcp).lower()
        os.environ["CODY_DEBUG"] = str(debug).lower()

        # 准备启动参数
        args = []
        binary = ""
        if test_against_node_source:
            binary = "node"
            args.extend(
                (
                    "--enable-source-maps",
                    "/home/prinova/CodeProjects/cody/agent/dist/index.js",
                )
            )
        else:
            binary = self.cody_binary
        args.append("api")
        args.append("jsonrpc-stdio")
        log_filename = f"log/cody_agent_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_filename), exist_ok=True)
        log_file = open(log_filename, 'wb')
        self._process: Process = await asyncio.create_subprocess_exec(
            binary,
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=log_file,
        )
        logger.info("创建了PID为%d的Cody代理进程", self._process.pid)
        self._reader = self._process.stdout
        self._writer = self._process.stdin

        if not self.use_tcp:
            logger.info("已创建与Cody代理的stdio连接")
        else:
            # TCP连接逻辑
            retry: int = 0
            retry_attempts: int = 5
            # TODO: 考虑使这些参数可配置
            host: str = "localhost"
            port: int = 3113
            for retry in range(retry_attempts):
                try:
                    (self._reader, self._writer) = await asyncio.open_connection(
                        host, port
                    )
                    if self._reader is not None and self._writer is not None:
                        logger.info(
                            "已创建与Cody代理的TCP连接 (%s:%s)",
                            host,
                            port,
                        )
                        break
                except ConnectionRefusedError as exc:
                    # TODO: 这不是最优雅的重试方式，但它保持了日志的简洁。考虑重构。
                    await asyncio.sleep(1)  # 短暂延迟后重试
                    retry += 1
                    if retry == retry_attempts:
                        logger.debug(
                            "尝试连接到%s:%s时耗尽了%d次重试机会",
                            retry_attempts,
                            host,
                            port,
                        )
                        raise ServerTCPConnectionError(
                            "无法连接到服务器: %s:%s", host, port
                        ) from exc
                    else:
                        logger.debug(
                            "连接到%s:%s失败，正在重试 (%d)",
                            host,
                            port,
                            retry,
                        )

    async def cleanup_server(self):
        """
        清理服务器连接。

        向服务器发送"shutdown"请求，并在服务器进程仍在运行时终止它。
        """
        logger.info("正在清理服务器...")
        await _send_jsonrpc_request(self._writer, "shutdown", None)
        if self._process.returncode is None:
            self._process.terminate()
        await self._process.wait()
