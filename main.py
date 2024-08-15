import asyncio
import logging
import os

from dotenv import load_dotenv

from codypy.agent import CodyAgent
from codypy.client_info import AgentSpecs, Models
from codypy.config import BLUE, GREEN, RESET
from codypy.context import append_paths
from codypy.server import CodyServer

# 加载环境变量
load_dotenv()
SRC_ACCESS_TOKEN = os.getenv("SRC_ACCESS_TOKEN")
BINARY_PATH = os.getenv("BINARY_PATH")

# 设置日志记录器
logger = logging.getLogger(__name__)


async def main():
    """
    主函数：（用于功能演示）初始化Cody服务器和代理，并运行交互式聊天循环。
    """
    # 设置全局日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # 创建CodyServer实例并使用指定的二进制路径和调试模式初始化
    logger.info("--- 创建服务器连接 ---")
    cody_server: CodyServer = await CodyServer.init(
        cody_binary_file=BINARY_PATH,
    )
    
    # 创建AgentSpecs实例，指定工作空间根URI和扩展配置
    agent_specs = AgentSpecs(
        # workspaceRootUri="./",  # 可以指定代码库路径，例如 "/home/prinova/CodeProjects/codypy"
        extensionConfiguration={
            "accessToken": SRC_ACCESS_TOKEN,
            "customConfiguration": {},
        },
    )
    
    # 使用指定的agent_specs初始化CodyAgent
    logger.info("--- 初始化代理 ---")
    cody_agent: CodyAgent = CodyAgent(cody_server=cody_server, agent_specs=agent_specs)
    await cody_agent.initialize_agent()
    
    # 获取并打印可用的聊天模型
    logger.info("--- 获取聊天模型 ---")
    models = await cody_agent.get_models(model_type="chat")
    logger.info("可用模型: %s", models)
    
    # 创建新的聊天会话
    logger.info("--- 创建新聊天 ---")
    await cody_agent.new_chat()
    
    # 设置聊天模型为Gemini15Flash
    logger.info("--- 设置模型 ---")
    await cody_agent.set_model(model=Models.Gemini15Flash)
    
    # # 设置仓库上下文（仅限企业版用户）
    # logger.info("--- 设置上下文仓库 ---")
    # await cody_agent.set_context_repo(repos=["github.com/fabric-of-tetrahedron/codypy"])
    
    # 设置要使用的指定上下文文件
    context_file = append_paths(
        "./main.py",
        # "./codypy/logger.py", # 这个文件不存在
    )
    
    # 开始交互式聊天循环
    logger.info("--- 发送消息（简短） ---")
    while True:
        message: str = input(f"{GREEN}人类:{RESET} ")
        response, context_files_response = await cody_agent.chat(
            message=message,
            enhanced_context=False,  # 设置为True以启用代码库感知
            show_context_files=True,  # 设置为True以返回推断的上下文文件（可选范围）
            context_files=context_file,  # 设置要提供上下文的文件列表
        )
        if response == "":
            break
        print(f"{BLUE}助手{RESET}: {response}\n")
        
        # 打印上下文文件信息
        logger.info("--- 上下文文件 ---")
        if context_files_response:
            for context in context_files_response:
                logger.info("文件: %s", context)
        else:
            logger.info("无上下文文件")
    
    # 清理服务器并返回None
    await cody_server.cleanup_server()
    return None


if __name__ == "__main__":
    asyncio.run(main())
