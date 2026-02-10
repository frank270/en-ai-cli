"""Rich 終端介面工具"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.styles import Style

console = Console()

# 決定歷史紀錄檔案路徑
HISTORY_FILE = Path.home() / ".en-ai" / "chat_history"
os.makedirs(HISTORY_FILE.parent, exist_ok=True)
history = FileHistory(str(HISTORY_FILE))

# 設定 prompt_toolkit 樣式與 Rich 保持一致
style = Style.from_dict({
    "prompt": "bold green",
    "info": "dim",
})

def print_success(message: str) -> None:
    """顯示成功訊息"""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """顯示錯誤訊息"""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str) -> None:
    """顯示警告訊息"""
    console.print(f"[yellow]⚠[/yellow]  {message}")


def print_info(message: str) -> None:
    """顯示資訊訊息"""
    console.print(f"[blue]ℹ[/blue]  {message}")


def print_header(title: str) -> None:
    """顯示標題"""
    console.print(f"\n[bold cyan]{title}[/bold cyan]\n")


def print_panel(content: str, title: str = "") -> None:
    """顯示面板"""
    console.print(Panel(content, title=title, border_style="cyan"))


def confirm(message: str, default: bool = False) -> bool:
    """
    確認提示
    
    Args:
        message: 提示訊息
        default: 預設值
        
    Returns:
        使用者選擇
    """
    return Confirm.ask(message, default=default)


def prompt(message: str, password: bool = False, default: str = "", show_default: bool = True) -> str:
    """
    輸入提示（使用 prompt_toolkit 以支援方向鍵與歷史紀錄）
    
    Args:
        message: 提示訊息
        password: 是否為密碼（隱藏輸入）
        default: 預設值
        show_default: 是否顯示預設值
        
    Returns:
        使用者輸入
    """
    # 轉換 Rich 的標記為 ANSI 以供 prompt_toolkit 顯示
    with console.capture() as capture:
        console.print(message, end="")
    prompt_text = ANSI(capture.get())
    
    try:
        user_input = pt_prompt(
            prompt_text,
            is_password=password,
            history=history,
            style=style,
        )
        # 如果使用者直接按 Enter 且有預設值
        if not user_input.strip() and default:
            return default
        return user_input
    except (KeyboardInterrupt, EOFError):
        # 讓上層處理中斷
        raise

def display_models_table(models: List[Dict[str, Any]]) -> None:
    """
    以表格形式顯示模型列表
    
    Args:
        models: 模型列表
    """
    table = Table(title="可用模型")
    
    table.add_column("模型 ID", style="cyan")
    table.add_column("名稱", style="white")
    table.add_column("上下文長度", justify="right", style="yellow")
    table.add_column("類型", style="green")
    
    for model in models:
        model_type = "Free" if model.get("is_free", False) else "Paid"
        type_style = "green" if model.get("is_free", False) else "red"
        
        table.add_row(
            model["id"],
            model.get("name", model["id"]),
            str(model.get("context_length", "N/A")),
            f"[{type_style}]{model_type}[/{type_style}]",
        )
    
    console.print(table)


def display_config_table(config: Dict[str, Any], scope: str) -> None:
    """
    以表格形式顯示配置
    
    Args:
        config: 配置字典
        scope: 作用域（workspace 或 global）
    """
    table = Table(title=f"{scope.capitalize()} 配置")
    
    table.add_column("鍵名", style="cyan")
    table.add_column("值", style="white")
    
    for key, value in config.items():
        # 隱藏 API key 的部分內容
        if "api_key" in key.lower() and isinstance(value, str) and len(value) > 10:
            display_value = value[:8] + "..." + value[-4:]
        else:
            display_value = str(value)
        
        table.add_row(key, display_value)
    
    console.print(table)
