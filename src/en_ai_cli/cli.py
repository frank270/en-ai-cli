"""CLI 命令入口"""

import click
from pathlib import Path

from en_ai_cli.core.config import ConfigManager, ConfigScope
from en_ai_cli.core.platform import PlatformDetector
from en_ai_cli.services.openrouter import OpenRouterClient
from en_ai_cli.ui import terminal as ui


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """En-Ai-Cli: 基於 CLI 的 AI 對話環境"""
    pass


@cli.command()
@click.option("--global", "is_global", is_flag=True, help="初始化全域配置")
def init(is_global: bool):
    """初始化 En-Ai-Cli 配置"""
    scope = ConfigScope.GLOBAL if is_global else ConfigScope.WORKSPACE
    scope_name = "全域" if is_global else "Workspace"
    
    ui.print_header(f"🎉 歡迎使用 En-Ai-Cli！")
    ui.print_info(f"正在初始化 {scope_name} 配置...")
    
    config = ConfigManager()
    
    # 輸入 API Key
    api_key = ui.prompt("📝 請輸入 OpenRouter API Key", password=True)
    
    if not api_key:
        ui.print_error("API Key 不能為空")
        return
    
    # 測試連線
    ui.print_info("正在驗證 API Key...")
    client = OpenRouterClient(api_key)
    
    if not client.test_connection():
        ui.print_error("API Key 驗證失敗，請檢查是否正確")
        return
    
    ui.print_success("API Key 驗證成功")
    
    # 取得模型列表
    ui.print_info("正在取得可用模型...")
    models = client.get_models()
    free_models = [m for m in models if m.is_free]
    paid_models = [m for m in models if not m.is_free]
    
    ui.print_info(f"找到 {len(free_models)} 個 free 模型，{len(paid_models)} 個付費模型")
    
    # 選擇模型策略
    ui.print_info("\n🤖 請選擇預設模型策略：")
    ui.console.print("  1. ✓ 優先使用 free 模型（推薦）")
    ui.console.print("  2.   允許使用付費模型")
    ui.console.print("  3.   手動選擇模型")
    
    choice = ui.prompt("\n選擇", default="1")
    
    prefer_free = True
    fallback_to_paid = False
    default_model = None
    
    if choice == "1":
        prefer_free = True
        fallback_to_paid = False
        default_model = client.select_best_model(prefer_free=True)
        ui.print_success("已設定為優先使用 free 模型")
    elif choice == "2":
        prefer_free = True
        fallback_to_paid = True
        default_model = client.select_best_model(prefer_free=True)
        ui.print_success("已設定為優先使用 free 模型，無 free 模型時使用付費模型")
    elif choice == "3":
        # 顯示 free 模型列表
        if free_models:
            ui.console.print("\n[cyan]Free 模型:[/cyan]")
            for i, model in enumerate(free_models[:10], 1):
                ui.console.print(f"  {i}. {model.id}")
            
            model_idx = int(ui.prompt("選擇模型編號", default="1")) - 1
            if 0 <= model_idx < len(free_models):
                default_model = free_models[model_idx].id
        else:
            ui.print_warning("沒有可用的 free 模型")
            default_model = client.select_best_model(prefer_free=False)
    
    if default_model:
        ui.print_success(f"預設模型: {default_model}")
    
    # 彩色模式
    color_mode = ui.confirm("\n🎨 是否啟用彩色模式?", default=True)
    
    # 儲存配置
    config.init_config(scope, {
        "openrouter_api_key": api_key,
        "prefer_free_models": prefer_free,
        "fallback_to_paid": fallback_to_paid,
        "default_model": default_model,
        "color_mode": color_mode,
        "auto_save_history": True,
        "max_context_messages": 50,
        "model_cache_ttl": 3600,
    })
    
    ui.print_success(f"\n✓ {scope_name} 配置初始化完成！")
    ui.print_info("使用 'en-ai chat' 開始對話")


@cli.group()
def config():
    """配置管理"""
    pass


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--global", "is_global", is_flag=True, help="設定全域配置")
def config_set(key: str, value: str, is_global: bool):
    """設定配置值"""
    scope = ConfigScope.GLOBAL if is_global else ConfigScope.WORKSPACE
    config = ConfigManager()
    
    # 嘗試轉換布林值
    if value.lower() in ("true", "false"):
        value = value.lower() == "true"
    # 嘗試轉換數字
    elif value.isdigit():
        value = int(value)
    
    config.set(key, value, scope)
    scope_name = "全域" if is_global else "workspace"
    ui.print_success(f"已設定 {scope_name} 配置: {key} = {value}")


@config.command("get")
@click.argument("key")
def config_get(key: str):
    """取得配置值"""
    config = ConfigManager()
    value = config.get(key)
    
    if value is None:
        ui.print_error(f"找不到配置: {key}")
    else:
        ui.console.print(f"{key} = {value}")


@config.command("list")
def config_list():
    """列出所有配置"""
    config = ConfigManager()
    all_config = config.list_all()
    
    if all_config["workspace"]:
        ui.display_config_table(all_config["workspace"], "workspace")
        ui.console.print()
    
    if all_config["global"]:
        ui.display_config_table(all_config["global"], "global")
    
    if not all_config["workspace"] and not all_config["global"]:
        ui.print_warning("尚未初始化配置，請執行 'en-ai init'")


@cli.group()
def models():
    """模型管理"""
    pass


@models.command("list")
@click.option("--free", is_flag=True, help="僅顯示 free 模型")
def models_list(free: bool):
    """列出可用模型"""
    config = ConfigManager()
    api_key = config.get("openrouter_api_key")
    
    if not api_key:
        ui.print_error("尚未設定 API Key，請執行 'en-ai init'")
        return
    
    ui.print_info("正在取得模型列表...")
    client = OpenRouterClient(api_key)
    
    try:
        models_list = client.get_free_models() if free else client.get_models()
        
        if not models_list:
            ui.print_warning("沒有可用的模型")
            return
        
        # 轉換為字典格式
        models_data = [
            {
                "id": m.id,
                "name": m.name,
                "context_length": m.context_length,
                "is_free": m.is_free,
            }
            for m in models_list
        ]
        
        ui.display_models_table(models_data)
        ui.print_info(f"\n共 {len(models_list)} 個模型")
        
    except Exception as e:
        ui.print_error(f"取得模型列表失敗: {str(e)}")


@cli.command()
def info():
    """顯示系統資訊"""
    platform = PlatformDetector.detect()
    shell = PlatformDetector.get_shell_name()
    config = ConfigManager()
    
    ui.print_header("系統資訊")
    
    info_data = {
        "平台": platform.value,
        "Shell": shell,
        "Workspace 模式": "是" if config.is_workspace_mode() else "否",
    }
    
    for key, value in info_data.items():
        ui.console.print(f"[cyan]{key}:[/cyan] {value}")


@cli.command()
def chat():
    """開始 AI 對話"""
    from en_ai_cli.core.session import SessionManager
    from en_ai_cli.core.executor import CommandExecutor
    from en_ai_cli.services.history import HistoryLogger, MessageRole
    from en_ai_cli.ui import prompts
    
    config = ConfigManager()
    
    # 檢查 API Key
    api_key = config.get("openrouter_api_key")
    if not api_key:
        ui.print_error("尚未設定 API Key，請執行 'en-ai init'")
        return
    
    # 初始化組件
    session_mgr = SessionManager(config)
    session_id = session_mgr.get_session_id()
    
    # 決定 sessions 目錄
    if config.is_workspace_mode():
        sessions_dir = Path.cwd() / ".en-ai" / "sessions"
    else:
        sessions_dir = Path.home() / ".en-ai" / "sessions"
    
    history = HistoryLogger(sessions_dir, session_id)
    executor = CommandExecutor()
    client = OpenRouterClient(api_key)
    
    # 顯示歡迎訊息
    ui.print_header("🤖 En-Ai-Cli 對話模式")
    ui.console.print(f"Session ID: [cyan]{session_id}[/cyan]")
    ui.console.print("輸入 'exit' 或 'quit' 離開，'stats' 查看統計資訊\n")
    
    # 對話主循環
    while True:
        try:
            # 檢查上下文限制
            if session_mgr.is_at_limit():
                # 已達上限，強制封存或清理
                ui.print_error(f"⚠️  上下文已達上限 ({session_mgr.max_messages} 則訊息）！")
                ui.console.print("\n必須執行以下操作之一：")
                ui.console.print("  [cyan]1.[/cyan] 封存當前對話並開新 session（推薦）")
                ui.console.print("  [cyan]2.[/cyan] 清理歷史訊息並繼續")
                
                choice = ui.prompt("選擇", default="1")
                
                if choice == "1":
                    new_session_id = prompts.archive_and_new_session(session_mgr, history)
                    session_id = new_session_id
                    history = HistoryLogger(sessions_dir, session_id)
                    ui.console.print()
                else:
                    history.clear()
                    ui.print_success("歷史訊息已清理")
                    ui.console.print()
                continue
            
            elif session_mgr.should_warn_limit():
                # 達到警告閾值（80%）
                new_session_id = prompts.show_context_warning(session_mgr, history)
                if new_session_id != session_id:
                    # 切換到新 session
                    session_id = new_session_id
                    history = HistoryLogger(sessions_dir, session_id)
                    ui.console.print()
            
            # 用戶輸入
            user_input = ui.prompt("[bold green]You[/bold green]").strip()
            
            if not user_input:
                continue
            
            # 處理特殊命令
            if user_input.lower() in ("exit", "quit"):
                ui.print_info("再見！👋")
                break
            
            if user_input.lower() == "stats":
                prompts.show_session_stats(session_mgr)
                continue
            
            # 記錄用戶訊息
            history.add_user_message(user_input)
            session_mgr.increment_message_count()
            
            # 取得上下文
            context_messages = history.get_context_messages(limit=10)
            
            # 呼叫 AI
            ui.print_info("思考中...")
            try:
                response = client.chat(context_messages)
                ai_message = response["choices"][0]["message"]["content"]
                
                # 記錄 AI 回應
                history.add_assistant_message(ai_message)
                session_mgr.increment_message_count()
                
                # 顯示 AI 回應
                ui.console.print(f"\n[bold cyan]Assistant[/bold cyan]:\n{ai_message}\n")
                
                # 檢查是否包含指令建議（簡單啟發式：以 $ 或包含常見指令關鍵字）
                if _contains_command_suggestion(ai_message):
                    command = _extract_command(ai_message)
                    if command and prompts.confirm_command_execution(command, executor):
                        # 執行指令
                        result = executor.execute_safe(command)
                        prompts.display_execution_result(result)
                        
                        # 記錄執行結果
                        metadata = {
                            "command": command,
                            "exit_code": result.exit_code,
                            "output": result.output,
                        }
                        status = "成功" if result.success else "失敗"
                        history.add_system_message(f"指令執行{status}", metadata)
                        session_mgr.increment_message_count()
                
            except Exception as e:
                ui.print_error(f"AI 回應錯誤: {str(e)}")
                continue
        
        except KeyboardInterrupt:
            ui.console.print("\n")
            if ui.confirm("確定要離開嗎？"):
                break
            ui.console.print()
        except EOFError:
            break


def _contains_command_suggestion(text: str) -> bool:
    """檢查文字是否包含指令建議"""
    # 簡單啟發式：包含程式碼區塊或常見指令關鍵字
    indicators = ["```", "$", "執行", "運行", "指令", "命令"]
    return any(indicator in text for indicator in indicators)


def _extract_command(text: str) -> str:
    """從 AI 回應中提取指令"""
    # 嘗試從程式碼區塊中提取
    if "```" in text:
        lines = text.split("\n")
        in_code_block = False
        command_lines = []
        
        for line in lines:
            if line.strip().startswith("```"):
                if in_code_block:
                    break
                in_code_block = True
                continue
            
            if in_code_block:
                line = line.strip()
                if line and not line.startswith("#"):
                    command_lines.append(line)
        
        if command_lines:
            return " ".join(command_lines)
    
    # 嘗試提取 $ 開頭的行
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("$"):
            return line[1:].strip()
    
    return ""


@cli.group()
def session():
    """Session 管理"""
    pass


@session.command("list")
def session_list():
    """列出所有 sessions"""
    from en_ai_cli.core.session import SessionManager
    from rich.table import Table
    
    config = ConfigManager()
    session_mgr = SessionManager(config)
    sessions = session_mgr.list_sessions()
    
    if not sessions:
        ui.print_warning("尚無任何 session")
        return
    
    # 創建表格
    table = Table(title="📋 Session 列表", show_header=True, header_style="bold cyan")
    table.add_column("Session ID", style="yellow", width=12)
    table.add_column("建立時間", style="blue", width=20)
    table.add_column("訊息數", justify="right", style="green", width=10)
    table.add_column("最後活動", style="magenta", width=20)
    table.add_column("狀態", justify="center", width=10)
    
    # 取得當前 session ID
    current_id = session_mgr.current_session.session_id if session_mgr.current_session else None
    
    # 填充表格資料
    for s in sessions:
        is_current = "✓ 當前" if s.session_id == current_id else ""
        table.add_row(
            s.session_id,
            s.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            str(s.message_count),
            s.last_activity.strftime("%Y-%m-%d %H:%M:%S"),
            is_current
        )
    
    ui.console.print(table)
    ui.print_info(f"\n總計：{len(sessions)} 個 sessions")


@session.command("switch")
@click.argument("session_id")
def session_switch(session_id: str):
    """切換到指定 session"""
    from en_ai_cli.core.session import SessionManager
    
    config = ConfigManager()
    session_mgr = SessionManager(config)
    
    if session_mgr.switch_session(session_id):
        ui.print_success(f"已切換到 session: {session_id}")
    else:
        ui.print_error(f"Session 不存在: {session_id}")


@session.command("stats")
@click.argument("session_id", required=False)
def session_stats(session_id: str):
    """顯示 session 統計資訊"""
    from en_ai_cli.core.session import SessionManager
    from en_ai_cli.ui import prompts
    
    config = ConfigManager()
    session_mgr = SessionManager(config)
    
    # 如果指定 session_id，先切換（臨時）
    if session_id:
        target_session = session_mgr.load_session(session_id)
        if not target_session:
            ui.print_error(f"Session 不存在: {session_id}")
            return
        # 臨時顯示該 session 的統計
        old_session = session_mgr._current_session
        session_mgr._current_session = target_session
        prompts.show_session_stats(session_mgr)
        session_mgr._current_session = old_session
    else:
        prompts.show_session_stats(session_mgr)


@session.command("new")
def session_new():
    """建立新 session"""
    from en_ai_cli.core.session import SessionManager
    
    config = ConfigManager()
    session_mgr = SessionManager(config)
    new_id = session_mgr.new_session()
    
    ui.print_success(f"已建立新 session: {new_id}")


@session.command("export")
@click.argument("output", type=click.Path(), required=False)
def session_export(output: str):
    """匯出當前 session 為 Markdown"""
    from en_ai_cli.core.session import SessionManager
    from en_ai_cli.services.history import HistoryLogger
    from datetime import datetime
    
    config = ConfigManager()
    session_mgr = SessionManager(config)
    session_id = session_mgr.get_session_id()
    
    # 決定輸出路徑
    if output:
        output_path = Path(output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"session_{session_id}_{timestamp}.md")
    
    # 決定 sessions 目錄
    if config.is_workspace_mode():
        sessions_dir = Path.cwd() / ".en-ai" / "sessions"
    else:
        sessions_dir = Path.home() / ".en-ai" / "sessions"
    
    history = HistoryLogger(sessions_dir, session_id)
    history.save_markdown(output_path)
    
    ui.print_success(f"Session 已匯出至: {output_path}")


@session.command("archive")
@click.option("--auto-new", is_flag=True, help="封存後自動建立新 session")
def session_archive(auto_new: bool):
    """封存當前 session"""
    from en_ai_cli.core.session import SessionManager
    
    config = ConfigManager()
    session_mgr = SessionManager(config)
    
    if not session_mgr.current_session:
        ui.print_warning("無活躍 session 可封存")
        return
    
    session_id = session_mgr.current_session.session_id
    
    # 執行封存
    archive_path = session_mgr.archive_session()
    
    if archive_path:
        ui.print_success(f"Session 已封存至: {archive_path}")
        
        # 如果設定自動建立新 session
        if auto_new:
            new_id = session_mgr.new_session()
            ui.print_success(f"已建立新 session: {new_id}")
    else:
        ui.print_error("封存失敗")


if __name__ == "__main__":
    cli()

