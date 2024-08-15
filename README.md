# codypy 🐍🤖

**This is a WIP (work-in-progress) project** 🚧👷‍♂️

`codypy` 是一个 Python 包装器，它通过与 [Sourcegraph Cody](https://github.com/sourcegraph/cody) 的 Cody-Agent 服务器建立连接，使用 JSON-RPC（远程过程调用）协议在 TCP/stdio 连接上进行通信。它允许异步发送和接收 JSON-RPC 消息。 📨📥

**注意 1：您需要在 [Sourcegraph](https://sourcegraph.com/) 注册一个账户并创建一个 API 密钥。**

**注意 2：该项目目前处于实验性的 alpha 阶段。API 和功能可能会在未来版本中发生更改和中断。** ⚠️🔧

## 特性

- 使用 TCP 套接字或通过 stdio 连接到服务器
- 向服务器发送 JSON-RPC 消息
- 接收和处理来自服务器的 JSON-RPC 消息
- 处理连接错误和超时
- 从 JSON-RPC 响应中提取方法和结果
- 支持使用 `asyncio` 库进行异步通信
- 如果有推断的上下文文件，可以选择显示行范围

## 要求

- Python 3.7+
- `asyncio` 库
- Cody Agent CLI 二进制文件将根据操作系统和架构自动从 https://github.com/sourcegraph/cody/releases 下载

## 安装

### 安装 Cody CLI

Cody CLI 是一个强大的命令行工具，可以在终端中使用 Cody 的功能。本教程将指导您如何安装和使用 Cody CLI。

#### 注意事项

- Cody CLI 目前处于实验阶段。
- Cody CLI 使用与 Cody IDE 插件相同的技术，但可在命令行中使用。
- 它可用于终端中的即兴探索或作为脚本的一部分来自动化工作流程。
- Cody CLI 对免费、专业和企业用户都可用。
- Cody CLI 仅适用于人类交互使用，其API使用模式与在编辑器中使用Cody类似。
  - Cody免费/专业版用户：任何大量使用（如自动化后台处理）都**可能导致您的账户被封禁**。如有任何问题，请与我们联系。
  - Cody企业版用户：请与您的内部Sourcegraph负责人和我们的团队联系，以获取使用建议，避免产生意外的LLM费用。

#### 前提条件

在安装 Cody CLI 之前，请确保您的系统满足以下要求：

- 已安装 Node.js `v20` 或更高版本
  - <https://nodejs.org/>
- 已安装 `npm`、`yarn`、`pnpm` 或等效的包管理器

#### 安装步骤

从 npm 安装 Cody CLI 的方法如下：

1. 使用 npm 安装：
   ```shell
   npm install -g @sourcegraph/cody
   ```

2. 或者，如果您使用 yarn：
   ```shell
   yarn global add @sourcegraph/cody
   ```

3. 如果您使用 pnpm：
   ```shell
   pnpm install -g @sourcegraph/cody
   ```

#### 验证安装

安装完成后，运行以下命令以确认安装成功：

```shell
cody help
```

#### Windows

0. 安装Cody CLI

1. 克隆该存储库：
   ```shell
   git clone https://github.com/PriNova/codypy.git
   ```

2. 进入项目目录：
   ```shell
   cd codypy
   ```

3. 确保已安装 Python 3.7 或更高版本：
   ```shell
   python --version
   ```

4. 安装 `setuptools`：
   ```shell
   pip install setuptools
   ```

5. `asyncio` 库已包含在 Python 标准库中，因此无需额外安装。

6. 创建并激活虚拟环境：
   ```shell
   python -m venv venv
   source venv/bin/activate
   ```

7. 从 `requirements.txt` 文件安装依赖项：
   ```shell
   pip install -r requirements.txt
   ```

8. 将提供的 `env.example` 文件重命名为 `.env`，并将 `SRC_ACCESS_TOKEN` 值设置为您的 API 密钥，将 `BINARY_PATH` 路径设置为应下载并访问 Cody Agent 二进制文件的位置。在 Linux 中使用以下命令重命名文件：
   ```shell
   mv env.example .env
   ```

9. 使用 `python main.py` 运行脚本。

您现在已准备好使用 codypy！

**您还可以通过 `pip install -e .` 以开发模式安装该包。**

## 作为库使用

1. 必须设置 'BINARY_PATH' 以下载或使用 agent 二进制文件
2. 必须将 'SRC_ACCESS_TOKEN' 环境变量设置为 Sourcegraph 账户的 API 令牌。
3. 在 'workspaceRootUri' 属性中设置您的工作区路径为本地的 GitHub 存储库。
4. 使用 `python main.py` 运行示例脚本。
5. 脚本将尝试连接到 Cody Agent。
6. 如果连接成功，它将向服务器发送初始化消息。
7. 然后脚本将接收并处理来自服务器的 JSON-RPC 消息。
8. 如果 `is_debugging` 设置为 `True`，它将提取并显示接收到的消息中的方法和结果。
9. 您将进入“聊天”模式，可以根据输入内容与 Cody Agent 进行对话，并获得增强的代码库上下文信息。
10. 脚本将继续接收消息，直到您输入 `/quit`。然后服务器将关闭连接。

## 作为 CLI 工具使用

如果按上述方式安装了该包，您还可以将 codypy 作为 CLI 工具使用。只需将 `SRC_ACCESS_TOKEN` 和 `BINARY_PATH` 导出到您的环境中，然后在终端中执行 `codypy-cli --help` 以查看可用选项和标志。

## 示例

有关初始化和聊天的示例，请参阅 [main.py](https://github.com/PriNova/codypy/blob/main/main.py) 文件。

该示例展示了如何使用完整的周期来建立与服务器的连接并处理 JSON-RPC 消息。

## 路线图

- [x] 改进 `receive_jsonrpc_messages()` 函数中 JSON-RPC 响应的解析和处理。
- [x] 增强 `initializing_message()` 函数中的初始化消息以包含其他客户端信息。
- [x] 实现可靠的日志记录功能以跟踪客户端-服务器通信。
- [x] 实现 CLI 工具。
- [x] 根据操作系统和架构下载 Cody Agent 二进制文件。
- [ ] 为 `codypy` 中的关键功能开发单元测试。
- [x] 创建使用 `codypy` 客户端库的文档和示例。
- [ ] 实现支持包含有关文件和文件夹的额外上下文的信息。
- [x] 配置存储库上下文。
- [x] 显示对话中的推断上下文文件。

## 许可证

包含的第三方代码的版权声明根据其各自的许可证授权。

该项目是根据 [MIT 许可证](LICENSE) 授权的。