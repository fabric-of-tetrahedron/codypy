import logging
from typing import Any

from codypy.client_info import AgentSpecs, Models
from codypy.exceptions import AgentAuthenticationError
from codypy.messaging import _show_last_message, request_response
from codypy.server import CodyServer
from codypy.server_info import CodyAgentInfo

logger = logging.getLogger(__name__)


class CodyAgent:
    """
    CodyAgent 类代表一个 Cody AI 代理。
    
    这个类负责与 Cody 服务器进行交互，管理聊天会话，处理代码仓库上下文，
    以及执行各种与 AI 代理相关的操作。
    """

    def __init__(
        self,
        cody_server: CodyServer,
        agent_specs: AgentSpecs,
    ) -> None:
        """
        初始化 CodyAgent 实例。

        参数:
            cody_server (CodyServer): Cody 服务器实例。
            agent_specs (AgentSpecs): 代理规格，包含代理的配置信息。
        """
        self._cody_server = cody_server
        self.chat_id: str | None = None  # 当前聊天会话的 ID
        self.repos: dict = {}  # 缓存仓库信息的字典
        self.current_repo_context: list[str] = []  # 当前使用的仓库上下文
        self.agent_specs = agent_specs

    async def initialize_agent(self) -> None:
        """
        初始化 Cody 代理。

        这个方法向代理发送一个"initialize"请求，并处理响应。
        它验证服务器的认证状态，并在成功时初始化代理。

        如果服务器未经认证，将引发 AgentAuthenticationError 异常。
        """

        async def _handle_response(response: Any) -> None:
            """
            处理初始化响应的内部函数。

            参数:
                response (Any): 服务器的响应数据。

            异常:
                AgentAuthenticationError: 如果代理未经认证则抛出此异常。
            """
            cody_agent_info: CodyAgentInfo = CodyAgentInfo.model_validate(response)
            logger.debug("CodyAgent 使用以下规格初始化: %s", self.agent_specs)
            logger.debug("CodyAgent 信息: %s", cody_agent_info)
            if not cody_agent_info.authenticated:
                await self._cody_server.cleanup_server()
                raise AgentAuthenticationError("CodyAgent 未经认证")
            logger.info("CodyAgent 初始化成功")

        response = await request_response(
            "initialize",
            self.agent_specs.model_dump(),
            self._cody_server._reader,
            self._cody_server._writer,
        )

        await _handle_response(response)

    async def new_chat(self):
        """
        创建一个新的聊天会话。

        这个方法向 Cody 代理服务器发送一个创建新聊天会话的请求，
        并将返回的会话 ID 保存在实例变量中。
        """

        response = await request_response(
            "chat/new",
            None,
            self._cody_server._reader,
            self._cody_server._writer,
        )

        logger.info("新的聊天会话 %s 已创建", response)
        self.chat_id = response

    async def _lookup_repo_ids(self, repos: list[str]) -> list[dict]:
        """
        查找仓库对象的 ID。

        这个方法通过仓库名称查找对应的仓库对象。结果会被缓存在 self.repos 字典中，
        以避免在更改上下文时进行额外的查找。

        参数:
            repos (list[str]): 需要查找的仓库名称列表。

        返回:
            list[dict]: 包含仓库信息的字典列表。
        """

        if repos_to_lookup := [x for x in repos if x not in self.repos]:
            response = await request_response(
                "graphql/getRepoIds",
                {"names": repos_to_lookup, "first": len(repos_to_lookup)},
                self._cody_server._reader,
                self._cody_server._writer,
            )

            for repo in response["repos"]:
                self.repos[repo["name"]] = repo
            for repo in repos:
                if repo not in self.repos:
                    self.repos[repo] = None

        return [self.repos[x] for x in repos if self.repos[x]]

    async def set_context_repo(self, repos: list[str]) -> None:
        """
        设置用作上下文的仓库。

        这个方法更新当前的仓库上下文，并将选定的仓库配置为聊天上下文。

        参数:
            repos (list[str]): 应该用作聊天上下文的仓库名称列表。
        """

        if self.current_repo_context == repos:
            return

        self.current_repo_context = repos

        repo_objects = await self._lookup_repo_ids(repos=repos)

        command = {
            "id": self.chat_id,
            "message": {
                "command": "context/choose-remote-search-repo",
                "explicitRepos": repo_objects,
            },
        }
        await request_response(
            "webview/receiveMessage",
            command,
            self._cody_server._reader,
            self._cody_server._writer,
        )

    async def get_models(self, model_type: str) -> Any:
        """
        获取指定类型的可用模型。

        参数:
            model_type (str): 模型类型，可以是 "chat" 或 "edit"。

        返回:
            Any: "chat/models" 请求的结果。
        """

        model = {"modelUsage": f"{model_type}"}
        return await request_response(
            "chat/models",
            model,
            self._cody_server._reader,
            self._cody_server._writer,
        )

    async def set_model(self, model: Models = Models.Claude3Sonnet) -> Any:
        """
        设置聊天会话使用的模型。

        参数:
            model (Models): 要使用的模型。默认为 Models.Claude3Sonnet。

        返回:
            Any: "webview/receiveMessage" 请求的结果。
        """

        command = {
            "id": f"{self.chat_id}",
            "message": {"command": "chatModel", "model": f"{model.value.model_id}"},
        }

        return await request_response(
            "webview/receiveMessage",
            command,
            self._cody_server._reader,
            self._cody_server._writer,
        )

    async def chat(
        self,
        message,
        enhanced_context: bool = True,
        show_context_files: bool = False,
        context_files=None,
    ):
        """
        向 Cody 服务器发送聊天消息并返回响应。

        参数:
            message (str): 要发送给 Cody 服务器的消息。
            enhanced_context (bool, optional): 是否在聊天消息请求中包含增强上下文。默认为 True。
            show_context_files (bool, optional): 是否显示上下文文件。默认为 False。
            context_files (list, optional): 上下文文件列表。默认为 None。

        返回:
            tuple: 包含响应文本和上下文文件的元组。
        """
        if context_files is None:
            context_files = []
        if message in ["/quit", "/bye", "/exit"]:
            return "", []

        chat_message_request = {
            "id": f"{self.chat_id}",
            "message": {
                "command": "submit",
                "text": message,
                "submitType": "user",
                "addEnhancedContext": enhanced_context,
                "contextFiles": context_files,
            },
        }

        result = await request_response(
            "chat/submitMessage",
            chat_message_request,
            self._cody_server._reader,
            self._cody_server._writer,
        )

        (speaker, response, context_files_response) = await _show_last_message(
            result,
            show_context_files,
        )
        if speaker == "" or response == "":
            logger.error("提交聊天消息失败: %s", result)
            return None
        return (response, context_files_response)
