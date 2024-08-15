import argparse
import asyncio
import os

from codypy import CodyServer, CodyAgent
from codypy.client_info import AgentSpecs


async def async_main():
    """
    异步主函数，处理命令行参数并初始化聊天。
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="Cody Agent Python CLI")
    parser.add_argument("chat", help="初始化聊天对话")
    parser.add_argument(
        "--binary_path",
        type=str,
        required=True,
        default=os.getenv("BINARY_PATH"),
        help="Cody Agent 二进制文件的路径。（必需）",
    )
    
    parser.add_argument(
        "--access_token",
        type=str,
        required=True,
        default=os.getenv("SRC_ACCESS_TOKEN"),
        help="Sourcegraph 访问令牌。（需要导出为 SRC_ACCESS_TOKEN 环境变量）（必需）",
    )
    parser.add_argument(
        "-m",
        "--message",
        type=str,
        required=True,
        help="要发送的聊天消息。（必需）",
    )
    parser.add_argument(
        "--workspace_root_uri",
        type=str,
        default=os.path.abspath(os.getcwd()),
        help=f"当前工作目录。默认值={os.path.abspath(os.getcwd())}",
    )
    
    parser.add_argument(
        "-ec",
        "--enhanced-context",
        type=bool,
        default=True,
        help="如果在 git 仓库中，使用增强上下文（需要配置远程仓库）。默认值=True",
    )
    parser.add_argument(
        "-sc",
        "--show-context",
        type=bool,
        default=False,
        help="显示从消息中推断的上下文文件（如果有）。默认值=True",
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    # 调用聊天函数
    await chat(args)


async def chat(args):
    """
    处理聊天逻辑的异步函数。

    参数:
    args: 包含命令行参数的对象
    """
    # 初始化 CodyServer
    cody_server: CodyServer = await CodyServer.init(
        cody_binary_file=args.binary_path,
        version="0.0.5b",
    )
    # 创建 AgentSpecs 实例，指定工作空间根 URI 和扩展配置
    agent_specs = AgentSpecs(
        workspaceRootUri=args.workspace_root_uri,
        extensionConfiguration={
            "accessToken": args.access_token,
            "codebase": "",  # 可以设置为特定的代码库，例如 "github.com/sourcegraph/cody"
            "customConfiguration": {},
        },
    )
    # 初始化 CodyAgent
    cody_agent: CodyAgent = await cody_server.initialize_agent(agent_specs=agent_specs)
    
    # 创建新的聊天会话
    await cody_agent.new_chat()
    
    # 发送聊天消息并获取响应
    response = await cody_agent.chat(
        message=args.message,
        enhanced_context=args.ec,
        show_context_files=args.sc,
    )
    if response == "":
        return
    print(response)
    
    # 清理服务器资源
    await cody_server.cleanup_server()
    return None


def main():
    """
    主函数，运行异步主函数。
    """
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
