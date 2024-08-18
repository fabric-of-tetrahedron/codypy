# 导入所需的模块
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Literal

from pydantic import BaseModel


class ExtensionConfiguration(BaseModel):
    """
    扩展配置类
    
    这个类定义了扩展的各种配置选项，包括访问令牌、服务器端点、代码库等。
    """
    accessToken: str = ""  # 访问令牌
    serverEndpoint: str = "https://sourcegraph.com"  # 服务器端点
    codebase: str | None = None  # 代码库
    proxy: str | None = None  # 代理设置

    customHeaders: Dict[str, str] = {}  # 自定义头部

    # anonymousUserID 是记录遥测事件的重要组成部分。
    # 目前为了向后兼容是可选的，但在连接到 Agent 时强烈建议设置此项。
    anonymousUserID: str | None = None

    autocompleteAdvancedProvider: str | None = None  # 高级自动完成提供者
    autocompleteAdvancedModel: str | None = None  # 高级自动完成模型
    debug: bool | None = None  # 调试模式
    verboseDebug: bool | None = None  # 详细调试模式

    # 当传递时，Agent 将处理记录事件。
    # 如果未传递，客户端必须手动发送 `graphql/logEvent` 请求。
    # @已弃用 这仅用于旧版 logEvent - 请使用 `telemetry` 代替。
    eventProperties: Dict | None = None

    customConfiguration: Dict | None = None  # 自定义配置


class ClientCapabilities(BaseModel):
    """
    客户端能力类
    
    定义了客户端支持的各种功能和能力。
    """
    completions: Literal["none"] = "none"  # 自动完成功能
    chat: Literal["none", "streaming"] = "none"  # 聊天功能
    git: Literal["none", "disabled"] = "none"  # Git 功能
    progressBars: Literal["none", "enabled"] = "none"  # 进度条功能
    edit: Literal["none", "enabled"] = "none"  # 编辑功能
    editWorkspace: Literal["none", "enabled"] = "none"  # 工作区编辑功能
    untitledDocuments: Literal["none", "enabled"] = "none"  # 未命名文档功能
    showDocument: Literal["none", "enabled"] = "none"  # 显示文档功能
    codeLenses: Literal["none", "enabled"] = "none"  # 代码镜头功能
    showWindowMessage: Literal["notification", "request"] = "notification"  # 显示窗口消息功能


class AgentSpecs(BaseModel):
    """
    代理规格类
    
    定义了代理的各种属性和配置。
    """
    name: str = "cody"  # 代理名称
    workspaceRootUri: str | None = None  # 工作区根 URI

    extensionConfiguration: ExtensionConfiguration | None = None  # 扩展配置
    capabilities: ClientCapabilities | None = None  # 客户端能力

    #
    # 可选的跟踪属性，用于注入到代理记录的遥测事件中。
    #
    # marketingTracking: TelemetryEventMarketingTrackingInput = None

    def __init__(
        self, name="cody", workspaceRootUri="", **data
    ):
        """
        初始化 AgentSpecs 实例
        
        :param name: 代理名称
        :param version: 代理版本
        :param workspaceRootUri: 工作区根 URI
        :param data: 其他数据
        """
        super().__init__(
            name=name, workspaceRootUri=workspaceRootUri, **data
        )
        self.name = name


@dataclass
class ModelSpec:
    """
    模型规格类
    
    定义了模型的各种属性。
    """
    model_name: str = ""  # 模型名称
    model_id: str = ""  # 模型 ID
    temperature: float = 0.0  # 温度参数
    maxTokensToSample: int = 512  # 最大采样令牌数


class Models(Enum):
    """
    模型枚举类
    
    定义了各种可用的模型及其规格。
    """
    Claude35Sonnet = ModelSpec(
        model_name="Claude 3.5 Sonnet",
        model_id="anthropic/claude-3-5-sonnet-20240620",
    )
    Claude3Sonnet = ModelSpec(
        model_name="Claude 3 Sonnet",
        model_id="anthropic/claude-3-sonnet-20240229",
    )
    Claude3Opus = ModelSpec(
        model_name="Claude 3 Opus",
        model_id="anthropic/claude-3-opus-20240229",
    )
    Claude3Haiku = ModelSpec(
        model_name="Claude 3 Haiku",
        model_id="anthropic/claude-3-haiku-20240307",
    )
    GPT4o = ModelSpec(
        model_name="GPT-4o",
        model_id="openai/gpt-4o",
    )
    GPT4TurboPreview = ModelSpec(
        model_name="GPT-4 Turbo",
        model_id="openai/gpt-4-turbo",
    )
    GPT35Turbo = ModelSpec(
        model_name="GPT-3.5 Turbo",
        model_id="openai/gpt-3.5-turbo",
    )
    Gemini15Pro = ModelSpec(
        model_name="Gemini 1.5 Pro",
        model_id="google/gemini-1.5-pro-latest",
    )
    Gemini15Flash = ModelSpec(
        model_name="Gemini 1.5 Flash",
        model_id="google/gemini-1.5-flash-latest",
    )
    Mixtral8x7b = ModelSpec(
        model_name="Mixtral 8x7B",
        model_id="fireworks/accounts/fireworks/models/mixtral-8x7b-instruct",
    )
    Mixtral8x22b = ModelSpec(
        model_name="Mixtral 8x22B",
        model_id="fireworks/accounts/fireworks/models/mixtral-8x22b-instruct",
    )
