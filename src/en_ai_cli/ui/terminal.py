"""Rich 終端介面工具"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from typing import List, Dict, Any


console = Console()


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


def prompt(message: str, password: bool = False, default: str = "") -> str:
    """
    輸入提示
    
    Args:
        message: 提示訊息
        password: 是否為密碼（隱藏輸入）
        default: 預設值
        
    Returns:
        使用者輸入
    """
    return Prompt.ask(message, password=password, default=default)


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
