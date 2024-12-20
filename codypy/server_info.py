# 导入 pydantic 库中的 BaseModel 类
from pydantic import BaseModel


# 定义 CodyLLM 站点配置模型
class CodyLLMSiteConfiguration(BaseModel):
    """
    CodyLLM 站点配置类

    属性:
    - chatModel: 聊天模型名称
    - chatModelMaxTokens: 聊天模型最大令牌数
    - fastChatModel: 快速聊天模型名称
    - fastChatModelMaxTokens: 快速聊天模型最大令牌数
    - completionModel: 补全模型名称
    - completionModelMaxTokens: 补全模型最大令牌数
    - provider: 提供商名称
    """
    chatModel: str | None = None  # 聊天模型名称，可为空
    chatModelMaxTokens: int | None = None  # 聊天模型最大令牌数，可为空
    fastChatModel: str | None = None  # 快速聊天模型名称，可为空
    fastChatModelMaxTokens: int | None = None  # 快速聊天模型最大令牌数，可为空
    completionModel: str | None = None  # 补全模型名称，可为空
    completionModelMaxTokens: int | None = None  # 补全模型最大令牌数，可为空
    provider: str | None = None  # 提供商名称，可为空


# 定义认证状态模型
class AuthStatus(BaseModel):
    """
    认证状态类

    属性:
    - endpoint: 端点 URL
    - isDotCom: 是否为 .com 域名
    - isLoggedIn: 是否已登录
    - showInvalidAccessTokenError: 是否显示无效访问令牌错误
    - authenticated: 是否已认证
    - hasVerifiedEmail: 是否有已验证的电子邮件
    - requiresVerifiedEmail: 是否需要验证电子邮件
    - siteHasCodyEnabled: 站点是否启用了 Cody
    - siteVersion: 站点版本
    - userCanUpgrade: 用户是否可以升级
    - username: 用户名
    - primaryEmail: 主要电子邮件地址
    - displayName: 显示名称
    - avatarURL: 头像 URL
    - configOverwrites: Cody LLM 站点配置覆盖
    """
    endpoint: str
    showInvalidAccessTokenError: bool
    authenticated: bool
    hasVerifiedEmail: bool
    requiresVerifiedEmail: bool
    siteVersion: str
    userCanUpgrade: bool
    username: str
    primaryEmail: str
    displayName: str | None = None
    avatarURL: str
    configOverwrites: CodyLLMSiteConfiguration | None = None


# 定义 Cody 代理信息模型
class CodyAgentInfo(BaseModel):
    """
    Cody 代理信息类

    属性:
    - name: 代理名称
    - authenticated: 是否已认证
    - codyEnabled: 是否启用 Cody
    - codyVersion: Cody 版本
    - authStatus: 认证状态
    """
    name: str  # 代理名称
    authenticated: bool | None = None  # 是否已认证，可为空
    codyEnabled: bool | None = None  # 是否启用 Cody，可为空
    codyVersion: str | None = None  # Cody 版本，可为空
    authStatus: AuthStatus | None = None  # 认证状态，可为空
