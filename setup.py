from setuptools import setup, find_packages

setup(
    name="en-ai-cli",
    version="0.4.0",
    description="基於 CLI 的 AI 對話環境，支援跨平台指令執行與互動式對話體驗",
    author="Your Name",
    author_email="you@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "click>=8.1.7",
        "rich>=13.7.0",
        "httpx>=0.27.0",
        "pydantic>=2.5.0",
        "prompt_toolkit>=3.0.43",
        "requests>=2.32.0",
    ],
    entry_points={
        "console_scripts": [
            "en-ai=en_ai_cli.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
