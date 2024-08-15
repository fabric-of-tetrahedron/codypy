# CodyPy异常类定义

class CodyPyError(Exception):
    """
    所有CodyPy异常的基类。
    
    这个类继承自Python的内置Exception类，用于创建CodyPy特定的异常层次结构。
    所有其他CodyPy相关的异常都应该继承自这个类。
    """
    pass


class AgentAuthenticationError(CodyPyError):
    """
    Cody代理认证错误异常。
    
    当Cody代理的认证过程失败时抛出此异常。
    这可能是由于无效的凭证、网络问题或服务器端的认证问题导致的。
    """

    def __init__(self, message="代理认证失败"):
        self.message = message
        super().__init__(self.message)


class AgentBinaryDownloadError(CodyPyError):
    """
    Cody代理二进制文件下载错误异常。
    
    当尝试下载Cody代理的二进制文件时遇到问题时抛出此异常。
    可能的原因包括网络连接问题、服务器错误或本地存储问题。
    """

    def __init__(self, message="下载Cody代理二进制文件失败"):
        self.message = message
        super().__init__(self.message)


class AgentBinaryNotFoundError(CodyPyError):
    """
    Cody代理二进制文件未找到异常。
    
    当系统无法找到所需的Cody代理二进制文件时抛出此异常。
    这可能是由于文件被删除、移动或下载失败导致的。
    """

    def __init__(self, message="未找到Cody代理二进制文件"):
        self.message = message
        super().__init__(self.message)


class ServerTCPConnectionError(CodyPyError):
    """
    服务器TCP连接错误异常。
    
    当尝试通过TCP连接到服务器时遇到问题时抛出此异常。
    可能的原因包括网络问题、服务器宕机或防火墙设置阻止了连接。
    """

    def __init__(self, message="无法通过TCP连接到服务器"):
        self.message = message
        super().__init__(self.message)
