# 导入必要的模块
from setuptools import find_packages, setup

# 读取 requirements.txt 文件的内容
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# 配置包的元数据和安装信息
setup(
    # 包名
    name="codypy",
    # 版本号
    version="0.1.2",
    # 简短描述
    description="一个Python包装器,通过TCP/stdio连接使用JSON-RPC协议与Sourcegraph Cody的Cody-Agent服务器建立连接。",
    # 长描述(从README.md读取)
    long_description=open("README.md").read(),
    # 长描述的内容类型
    long_description_content_type="text/markdown",
    # 作者
    author="PriNova",
    # 作者邮箱
    author_email="info@prinova.de",
    # 项目URL
    url="https://github.com/PriNova/codypy",
    # 自动查找包
    packages=find_packages(),
    # 定义命令行入口点
    entry_points={
        "console_scripts": [
            "codypy-cli = cli:main",
        ],
    },
    # 安装依赖
    install_requires=requirements,
    # 包的分类信息
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: MIT License",
        "Programming Language :: Python :: 3.12",
    ],
    # Python版本要求
    python_requires=">=3.7",
)

"""
中文文档:

这个setup.py文件用于配置Python包的安装和分发信息。主要功能包括:

1. 定义包的基本信息(名称、版本、描述等)
2. 指定包的依赖关系
3. 设置命令行工具入口点
4. 定义包的分类信息和Python版本要求

使用setuptools的setup函数来配置这些信息。该配置允许使用pip安装此包,
并提供了codypy-cli命令行工具。

包的依赖关系从requirements.txt文件中读取,确保安装时所有必要的依赖都被正确安装。
"""