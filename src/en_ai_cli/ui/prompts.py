"""互動提示介面：處理用戶確認和互動"""

from rich.panel import Panel
from rich.prompt import Confirm
from rich.syntax import Syntax
from pathlib import Path

from en_ai_cli.ui.terminal import console, print_warning, print_info, prompt
from en_ai_cli.core.executor import CommandExecutor, ExecutionResult
from en_ai_cli.core.session import SessionManager
from en_ai_cli.services.history import HistoryLogger
from datetime import datetime


def confirm_command_execution(command: str, executor: CommandExecutor) -> bool:
    """
    確認是否執行指令
    
    Args:
        command: 要執行的指令
        executor: 指令執行器
        
    Returns:
        True 如果用戶確認執行
    """
    # 顯示指令
    syntax = Syntax(command, "bash", theme="monokai", line_numbers=False)
    console.print("\n💡 建議執行以下指令：")
    console.print(Panel(syntax, title="指令", border_style="cyan"))
    
    # 檢查是否危險
    if executor.is_dangerous(command):
        print_warning("⚠️  此指令可能有風險，請仔細確認！")
    
    # 檢查是否需要權限
    if executor.requires_privilege(command):
        print_info("ℹ️  此指令需要管理員權限")
    
    # 詢問確認
    return Confirm.ask("\n是否執行此指令？", default=False)


def display_execution_result(result: ExecutionResult) -> None:
    """
    顯示指令執行結果
    
    Args:
        result: 執行結果
    """
    if result.success:
        console.print("\n[green]✓[/green] 指令執行成功")
        if result.stdout:
            console.print(Panel(
                result.stdout[:1000],  # 限制顯示長度
                title="輸出",
                border_style="green"
            ))
    else:
        console.print(f"\n[red]✗[/red] 指令執行失敗（退出碼: {result.exit_code}）")
        if result.stderr:
            console.print(Panel(
                result.stderr[:1000],
                title="錯誤輸出",
                border_style="red"
            ))


def show_context_warning(session_mgr: SessionManager, history: HistoryLogger) -> str:
    """
    顯示上下文警告並處理用戶選擇
    
    Args:
        session_mgr: Session 管理器
        history: 歷程記錄器
        
    Returns:
        新的 session ID（如果有切換）或當前 session ID
    """
    current = session_mgr.get_message_count()
    max_msg = session_mgr.max_messages
    percentage = session_mgr.get_usage_percentage()
    
    print_warning(f"⚠️  上下文即將達到限制 ({current}/{max_msg}, {percentage:.0f}%)")
    console.print("\n建議操作：")
    console.print("  [cyan]1.[/cyan] 封存當前對話並開新 session（推薦）")
    console.print("  [cyan]2.[/cyan] 繼續對話（可能影響 AI 回應品質）")
    console.print("  [cyan]3.[/cyan] 手動清理歷史訊息")
    
    choice = prompt("\n選擇", default="1")
    
    if choice == "1":
        # 封存對話
        return archive_and_new_session(session_mgr, history)
    elif choice == "3":
        # 清理歷史
        history.clear()
        console.print("[green]✓[/green] 歷史訊息已清理")
        return session_mgr.get_session_id()
    else:
        # 繼續對話
        return session_mgr.get_session_id()


def archive_and_new_session(session_mgr: SessionManager, history: HistoryLogger) -> str:
    """
    封存當前對話並建立新 session
    
    Args:
        session_mgr: Session 管理器
        history: 歷程記錄器
        
    Returns:
        新的 session ID
    """
    old_session_id = session_mgr.get_session_id()
    
    # 生成封存檔案路徑
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_filename = f"session_{old_session_id}_{timestamp}.md"
    
    # 決定封存位置（根據 workspace 模式）
    from en_ai_cli.core.config import ConfigManager
    config = ConfigManager()
    
    if config.is_workspace_mode():
        archive_dir = Path.cwd() / ".en-ai" / "archives"
    else:
        archive_dir = Path.home() / ".en-ai" / "archives"
    
    archive_path = archive_dir / archive_filename
    
    # 儲存封存
    history.save_markdown(archive_path)
    console.print(f"[green]✓[/green] 對話已封存至: [cyan]{archive_path}[/cyan]")
    
    # 建立新 session
    new_session_id = session_mgr.new_session()
    console.print(f"[green]✓[/green] 已切換到新 session: [cyan]{new_session_id}[/cyan]")
    
    return new_session_id


def show_session_stats(session_mgr: SessionManager) -> None:
    """
    顯示 session 統計資訊
    
    Args:
        session_mgr: Session 管理器
    """
    info = session_mgr.get_session_info()
    
    from rich.table import Table
    
    table = Table(title="Session 統計資訊")
    table.add_column("項目", style="cyan")
    table.add_column("值", style="white")
    
    table.add_row("Session ID", info["session_id"])
    table.add_row("建立時間", info["created_at"])
    table.add_row("訊息數量", str(info["message_count"]))
    table.add_row("上限", str(info["max_messages"]))
    table.add_row("剩餘", str(info["remaining"]))
    table.add_row("使用率", f"{info['usage_percentage']:.1f}%")
    table.add_row("最後活動", info["last_activity"])
    
    console.print(table)


def prompt_multiline(message: str = "輸入訊息（輸入空行結束）") -> str:
    """
    多行輸入提示
    
    Args:
        message: 提示訊息
        
    Returns:
        用戶輸入的多行文字
    """
    console.print(f"[cyan]{message}[/cyan]")
    lines = []
    
    while True:
        try:
            line = input()
            if not line:  # 空行表示結束
                break
            lines.append(line)
        except (KeyboardInterrupt, EOFError):
            break
    
    return "\n".join(lines)
