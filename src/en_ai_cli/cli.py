"""CLI 命令入口"""

import click
from pathlib import Path
from typing import Optional

from en_ai_cli.core.config import ConfigManager, ConfigScope
from en_ai_cli.core.platform import PlatformDetector
from en_ai_cli.services.openrouter import OpenRouterProvider
from en_ai_cli.services.provider_manager import ProviderManager
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
    from en_ai_cli.services.ollama import OllamaProvider
    
    scope = ConfigScope.GLOBAL if is_global else ConfigScope.WORKSPACE
    scope_name = "全域" if is_global else "Workspace"
    
    ui.print_header(f"🎉 歡迎使用 En-Ai-Cli！")
    ui.print_info(f"正在初始化 {scope_name} 配置...\n")
    
    config = ConfigManager()
    config_data = {}
    
    # 1. 偵測 Ollama
    ui.print_info("🔍 正在偵測本地 Ollama...")
    ollama_config = {
        "ollama_endpoint": "http://localhost:11434",
        "ollama_default_model": "qwen2.5-coder:3b",
    }
    ollama = OllamaProvider(ollama_config)
    ollama_available = ollama.is_available()
    
    if ollama_available:
        ui.print_success("✓ 偵測到 Ollama 正在執行")
        version = ollama.get_version()
        if version:
            ui.console.print(f"  版本: {version}")
        
        # 取得已安裝的模型
        try:
            ollama_models = ollama.list_models()
            if ollama_models:
                ui.console.print(f"  已安裝 {len(ollama_models)} 個模型")
        except:
            ollama_models = []
        
        # 詢問是否使用 Ollama
        use_ollama = ui.confirm("\n是否將 Ollama 設為預設 provider？", default=True)
        
        if use_ollama:
            config_data["preferred_provider"] = "ollama"
            config_data.update(ollama_config)
            
            # 讓用戶選擇預設模型
            if ollama_models:
                ui.console.print("\n[cyan]Ollama 已安裝的模型:[/cyan]")
                for i, model in enumerate(ollama_models[:10], 1):
                    ui.console.print(f"  {i}. {model.id}")
                
                model_choice = ui.prompt("選擇預設模型編號（直接按 Enter 使用預設）", default="")
                if model_choice and model_choice.isdigit():
                    model_idx = int(model_choice) - 1
                    if 0 <= model_idx < len(ollama_models):
                        config_data["ollama_default_model"] = ollama_models[model_idx].id
            
            ui.print_success(f"\n✓ 已設定使用 Ollama")
            ui.print_info("  （如需使用 OpenRouter，可稍後執行 'en-ai provider switch openrouter'）")
            
            # 還是可以選擇性設定 OpenRouter 作為備援
            setup_openrouter = ui.confirm("\n是否同時設定 OpenRouter（作為備援）？", default=False)
            if not setup_openrouter:
                # 跳到最後的通用設定
                config_data["color_mode"] = ui.confirm("\n🎨 是否啟用彩色模式？", default=True)
                config_data["auto_save_history"] = True
                config_data["max_context_messages"] = 50
                config_data["model_cache_ttl"] = 3600
                
                config.init_config(scope, config_data)
                ui.print_success(f"\n✓ {scope_name} 配置初始化完成！")
                ui.print_info("使用 'en-ai chat' 開始對話")
                return
    else:
        ui.print_warning("✗ 未偵測到 Ollama")
        ui.console.print("  如需使用 Ollama，請先安裝並啟動：https://ollama.ai\n")
        config_data["preferred_provider"] = "openrouter"
    
    # 2. 設定 OpenRouter
    ui.print_info("📝 設定 OpenRouter")
    api_key = ui.prompt("請輸入 OpenRouter API Key（直接按 Enter 跳過）", password=True, default="")
    
    if api_key:
        # 測試連線
        ui.print_info("正在驗證 API Key...")
        openrouter_config = {
            "openrouter_api_key": api_key,
            "prefer_free_models": True,
        }
        client = OpenRouterProvider(openrouter_config)
        
        if not client.is_available():
            ui.print_error("API Key 驗證失敗，請檢查是否正確")
            if not ollama_available:
                ui.print_error("沒有可用的 provider，初始化失敗")
                return
            ui.print_warning("將僅使用 Ollama")
        else:
            ui.print_success("API Key 驗證成功")
            config_data["openrouter_api_key"] = api_key
            
            # 取得模型列表
            ui.print_info("正在取得可用模型...")
            try:
                models = client.list_models()
                free_models = [m for m in models if m.is_free]
                paid_models = [m for m in models if not m.is_free]
                
                ui.print_info(f"找到 {len(free_models)} 個 free 模型，{len(paid_models)} 個付費模型")
                
                # 選擇模型策略
                ui.print_info("\n🤖 OpenRouter 模型策略：")
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
                
                config_data["prefer_free_models"] = prefer_free
                config_data["fallback_to_paid"] = fallback_to_paid
                if default_model:
                    config_data["openrouter_default_model"] = default_model
                    ui.print_success(f"預設模型: {default_model}")
            
            except Exception as e:
                ui.print_warning(f"取得模型列表失敗: {str(e)}")
    else:
        if not ollama_available:
            ui.print_error("未設定任何 provider，初始化失敗")
            ui.print_info("請至少設定 Ollama 或 OpenRouter 其中一個")
            return
    
    # 3. 角色設定
    ui.print_info("\n🎭 選擇初始角色 (Role)")
    from en_ai_cli.core.config import DEFAULT_ROLES
    role_names = list(DEFAULT_ROLES.keys())
    for i, name in enumerate(role_names, 1):
        ui.console.print(f"  {i}. {name}")
    
    role_choice = ui.prompt("選擇角色編號", default="1")
    if role_choice.isdigit():
        idx = int(role_choice) - 1
        if 0 <= idx < len(role_names):
            config_data["active_role"] = role_names[idx]

    # 4. 通用設定
    color_mode = ui.confirm("\n🎨 是否啟用彩色模式？", default=True)
    config_data["color_mode"] = color_mode
    config_data["auto_save_history"] = True
    config_data["max_context_messages"] = 50
    config_data["model_cache_ttl"] = 3600
    
    # 儲存配置
    config.init_config(scope, config_data)
    
    ui.print_success(f"\n✓ {scope_name} 配置初始化完成！")
    
    # 顯示摘要
    ui.print_info("\n📋 配置摘要：")
    ui.console.print(f"  Provider: {config_data.get('preferred_provider', 'openrouter')}")
    if config_data.get("preferred_provider") == "ollama":
        ui.console.print(f"  Ollama 模型: {config_data.get('ollama_default_model')}")
    if config_data.get("openrouter_api_key"):
        ui.console.print(f"  OpenRouter: 已設定")
    
    ui.print_info("\n使用 'en-ai chat' 開始對話")


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
@click.option("--provider", type=str, help="指定 provider（ollama 或 openrouter）")
def models_list(free: bool, provider: str):
    """列出可用模型"""
    config = ConfigManager()
    config_dict = {}
    
    # 載入完整配置
    if config.global_path.exists():
        config_dict = config._load_config(config.global_path)
    if config.workspace_path.exists():
        workspace_config = config._load_config(config.workspace_path)
        config_dict.update(workspace_config)
    
    manager = ProviderManager(config_dict)
    
    # 決定要顯示哪些 providers
    if provider:
        providers_to_show = [provider]
    else:
        # 顯示所有可用的 providers
        providers_to_show = manager.get_available_providers()
    
    if not providers_to_show:
        ui.print_error("沒有可用的 provider，請檢查配置")
        return
    
    # 依次顯示每個 provider 的模型
    for provider_name in providers_to_show:
        provider_obj = manager.get_provider(provider_name)
        
        if not provider_obj:
            continue
        
        ui.print_header(f"Provider: {provider_name}")
        
        try:
            models_list_data = provider_obj.list_models()
            
            if free:
                models_list_data = [m for m in models_list_data if m.is_free]
            
            if not models_list_data:
                ui.print_warning("沒有可用的模型")
                continue
            
            # 轉換為字典格式
            models_data = [
                {
                    "id": m.id,
                    "name": m.name,
                    "context_length": m.context_length or 0,
                    "is_free": m.is_free,
                }
                for m in models_list_data
            ]
            
            ui.display_models_table(models_data)
            ui.print_info(f"共 {len(models_list_data)} 個模型\n")
            
        except Exception as e:
            ui.print_error(f"取得 {provider_name} 模型列表失敗: {str(e)}\n")


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


@cli.group()
def provider():
    """Provider 管理"""
    pass


@provider.command("list")
def provider_list():
    """列出所有可用的 providers"""
    config = ConfigManager()
    config_dict = {}
    
    # 載入完整配置
    if config.global_path.exists():
        config_dict = config._load_config(config.global_path)
    if config.workspace_path.exists():
        workspace_config = config._load_config(config.workspace_path)
        config_dict.update(workspace_config)
    
    manager = ProviderManager(config_dict)
    all_providers = manager.list_all_providers()
    preferred = config_dict.get("preferred_provider", "ollama")
    
    ui.print_header("可用的 Providers")
    
    for name, status in all_providers.items():
        is_preferred = name == preferred
        prefix = "→ " if is_preferred else "  "
        
        if status["exists"]:
            if status["available"]:
                status_icon = "✓"
                status_text = "[green]可用[/green]"
            else:
                status_icon = "✗"
                status_text = "[red]不可用[/red]"
            
            ui.console.print(
                f"{prefix}[cyan]{name}[/cyan] {status_icon} {status_text}"
            )
            
            if status["available"] and status.get("default_model"):
                ui.console.print(f"      預設模型: {status['default_model']}")
        else:
            ui.console.print(f"{prefix}[dim]{name}[/dim] [dim]未設定[/dim]")
    
    ui.console.print(f"\n當前 provider: [cyan]{preferred}[/cyan]")


@provider.command("status")
@click.argument("name", required=False)
def provider_status(name: str):
    """顯示 provider 詳細狀態"""
    config = ConfigManager()
    config_dict = {}
    
    # 載入完整配置
    if config.global_path.exists():
        config_dict = config._load_config(config.global_path)
    if config.workspace_path.exists():
        workspace_config = config._load_config(config.workspace_path)
        config_dict.update(workspace_config)
    
    manager = ProviderManager(config_dict)
    
    if not name:
        # 顯示當前 provider
        name = config_dict.get("preferred_provider", "ollama")
    
    status = manager.get_provider_status(name)
    
    if not status["exists"]:
        ui.print_error(f"未知的 provider: {name}")
        return
    
    ui.print_header(f"Provider: {name}")
    
    ui.console.print(f"狀態: {'[green]✓ 可用[/green]' if status['available'] else '[red]✗ 不可用[/red]'}")
    ui.console.print(f"配置有效: {'[green]是[/green]' if status['config_valid'] else '[red]否[/red]'}")
    
    if status.get("default_model"):
        ui.console.print(f"預設模型: {status['default_model']}")
    
    # 顯示相關配置
    if name == "ollama":
        endpoint = config_dict.get("ollama_endpoint", "http://localhost:11434")
        ui.console.print(f"端點: {endpoint}")
        
        # 嘗試取得版本資訊
        if status["available"]:
            from en_ai_cli.services.ollama import OllamaProvider
            provider = OllamaProvider(config_dict)
            version = provider.get_version()
            if version:
                ui.console.print(f"版本: {version}")
    
    elif name == "openrouter":
        has_key = bool(config_dict.get("openrouter_api_key"))
        ui.console.print(f"API Key: {'[green]已設定[/green]' if has_key else '[red]未設定[/red]'}")


@provider.command("switch")
@click.argument("name")
@click.option("--global", "is_global", is_flag=True, help="設定全域配置")
def provider_switch(name: str, is_global: bool):
    """切換到指定的 provider"""
    config = ConfigManager()
    config_dict = {}
    
    # 載入完整配置
    if config.global_path.exists():
        config_dict = config._load_config(config.global_path)
    if config.workspace_path.exists():
        workspace_config = config._load_config(config.workspace_path)
        config_dict.update(workspace_config)
    
    manager = ProviderManager(config_dict)
    
    try:
        manager.switch_provider(name)
        
        # 儲存配置
        scope = ConfigScope.GLOBAL if is_global else ConfigScope.WORKSPACE
        config.set("preferred_provider", name, scope)
        
        ui.print_success(f"已切換到 provider: {name}")
    except ValueError as e:
        ui.print_error(str(e))


@cli.group()
def role():
    """角色管理 (Persona Management)"""
    pass


@role.command("list")
def role_list():
    """列出所有角色"""
    from rich.table import Table
    config = ConfigManager()
    active_role = config.get_active_role_name()
    roles = config.get_roles()
    
    table = Table(title="角色列表")
    table.add_column("名稱", style="cyan")
    table.add_column("狀態", style="green")
    table.add_column("System Prompt", style="white", overflow="ellipsis", max_width=50)
    
    for name, data in roles.items():
        status = "[bold yellow]Active[/bold yellow]" if name == active_role else ""
        prompt = data.get("system_prompt", "").replace("\n", " ")
        table.add_row(name, status, prompt)
    
    ui.console.print(table)


@role.command("set")
@click.argument("name")
@click.option("--global", "is_global", is_flag=True, help="設定全域角色")
def role_set(name: str, is_global: bool):
    """切換當前角色"""
    config = ConfigManager()
    roles = config.get_roles()
    
    if name not in roles:
        ui.print_error(f"找不到角色: {name}")
        ui.print_info("請使用 'en-ai role list' 查看可用角色")
        return
    
    scope = ConfigScope.GLOBAL if is_global else ConfigScope.WORKSPACE
    config.set("active_role", name, scope)
    ui.print_success(f"已切換至角色: {name}")


@role.command("add")
@click.argument("name")
@click.option("--prompt", "-p", help="System Prompt 內容")
@click.option("--global", "is_global", is_flag=True, help="儲存至全域")
def role_add(name: str, prompt: Optional[str], is_global: bool):
    """新增角色"""
    config = ConfigManager()
    
    if not prompt:
        prompt = ui.prompt(f"請輸入角色 '{name}' 的 System Prompt")
    
    scope = ConfigScope.GLOBAL if is_global else ConfigScope.WORKSPACE
    roles = config.get("roles", {})
    roles[name] = {"system_prompt": prompt}
    config.set("roles", roles, scope)
    ui.print_success(f"角色 '{name}' 已新增")


@role.command("show")
@click.argument("name")
def role_show(name: str):
    """顯示角色詳細資訊"""
    from rich.panel import Panel
    config = ConfigManager()
    roles = config.get_roles()
    
    if name not in roles:
        ui.print_error(f"找不到角色: {name}")
        return
    
    role_data = roles[name]
    ui.print_header(f"角色: {name}")
    ui.console.print(Panel(role_data.get("system_prompt", ""), title="System Prompt", border_style="cyan"))


@role.command("delete")
@click.argument("name")
@click.option("--global", "is_global", is_flag=True, help="從全域刪除")
def role_delete(name: str, is_global: bool):
    """刪除角色"""
    if name == "default":
        ui.print_error("無法刪除預設角色 (default)")
        return
        
    config = ConfigManager()
    active_role = config.get_active_role_name()
    if name == active_role:
        ui.print_warning(f"角色 '{name}' 正處於活躍狀態，刪除前請先切換。")
        return
        
    scope = ConfigScope.GLOBAL if is_global else ConfigScope.WORKSPACE
    
    # 讀取特定作用域的配置，避免刪除 wrong scope
    config_path = config.workspace_path if scope == ConfigScope.WORKSPACE else config.global_path
    if not config_path.exists():
        ui.print_error(f"找不到 {scope} 配置文件")
        return
        
    config_data = config._load_config(config_path)
    roles = config_data.get("roles", {})
    
    if name not in roles:
        ui.print_error(f"在 {scope} 設定中找不到角色 '{name}'")
        return
        
    if ui.confirm(f"確定要刪除角色 '{name}' 嗎？"):
        del roles[name]
        config.set("roles", roles, scope)
        ui.print_success(f"角色 '{name}' 已刪除")


@cli.command()
def chat():
    """開始 AI 對話"""
    from en_ai_cli.core.session import SessionManager
    from en_ai_cli.core.executor import CommandExecutor
    from en_ai_cli.services.history import HistoryLogger, MessageRole
    from en_ai_cli.services.llm_provider import ChatMessage
    from en_ai_cli.ui import prompts
    
    config = ConfigManager()
    config_dict = {}
    
    # 載入完整配置
    if config.global_path.exists():
        config_dict = config._load_config(config.global_path)
    if config.workspace_path.exists():
        workspace_config = config._load_config(config.workspace_path)
        config_dict.update(workspace_config)
    
    # 初始化 Provider Manager
    try:
        manager = ProviderManager(config_dict)
        provider = manager.get_current_provider()
    except RuntimeError as e:
        ui.print_error(str(e))
        ui.print_info("\n請執行 'en-ai init' 初始化配置")
        return
    
    # 初始化組件
    session_mgr = SessionManager(config)
    
    # 檢查是否有角色設定 (針對舊版升級用戶)
    if not config.get("roles") or not config.get("active_role"):
        if ui.confirm("🔎 偵測到您尚未初始化角色設定，是否要套用預設角色組合？"):
            config.set("roles", config._get_default_config()["roles"])
            config.set("active_role", "default")
            ui.print_success("✓ 已將預設角色寫入配置檔案")

    session_id = session_mgr.get_session_id()
    
    # 決定 sessions 目錄
    if config.is_workspace_mode():
        sessions_dir = Path.cwd() / ".en-ai" / "sessions"
    else:
        sessions_dir = Path.home() / ".en-ai" / "sessions"
    
    history = HistoryLogger(sessions_dir, session_id)
    executor = CommandExecutor()
    
    # 顯示歡迎訊息
    ui.print_header("🤖 En-Ai-Cli 對話模式")
    ui.console.print(f"Session ID: [cyan]{session_id}[/cyan]")
    ui.console.print(f"Role: [yellow]{session_mgr.current_session.role}[/yellow]")
    ui.console.print(f"Provider: [cyan]{provider.get_provider_name()}[/cyan]")
    
    # 提示角色資訊
    active_role = config.get_active_role_name()
    ui.console.print(f"⚙️  已載入 [bold yellow]{active_role}[/bold yellow] 角色的專屬系統提示詞")
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
            
            # 用戶輸入（顯示訊息計數）
            count_info = f"{session_mgr.current_session.message_count}/{session_mgr.max_messages}"
            user_input = ui.prompt(f"[bold green]You[/bold green] [dim]({count_info})[/dim]", show_default=False).strip()
            
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
            
            # 取得上下文並轉換為 ChatMessage 格式
            context_messages_dict = history.get_context_messages(limit=10)
            context_messages = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in context_messages_dict
            ]
            
            # 加入系統提示詞（在訊息列表開頭）
            system_prompt = ChatMessage(
                role="system",
                content=config.get_active_role_prompt()
            )
            context_messages.insert(0, system_prompt)
            
            # 呼叫 AI
            ui.print_info("思考中...")
            try:
                response = provider.chat_completion(context_messages)
                ai_message = response.content
                
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
                        result = executor.execute(command)
                        prompts.display_execution_result(result)
                        
                        # 如果是 cd 指令成功，顯示當前路徑
                        if command.startswith("cd ") and result.success:
                            import os
                            ui.console.print(f"📂 當前路徑已變更為: [bold cyan]{os.getcwd()}[/bold cyan]\n")
                        
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
                # 移除行尾註解與多餘空格
                line = line.split("#")[0].strip()
                if line:
                    command_lines.append(line)
        
        if command_lines:
            # 使用 && 連接多行指令，確保順序執行
            return " && ".join(command_lines)
    
    # 嘗試提取 $ 開頭的行
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("$"):
            # 同樣移除行尾註解
            cmd = line[1:].split("#")[0].strip()
            return cmd
    
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

