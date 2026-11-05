#!/usr/bin/env python3
"""
Agent 团队创建器 - 支持预设模板
用法: python team_creator.py --template default
      python team_creator.py --agents "pm,ui,coding"
"""

import subprocess
import sys
import os
import argparse
import json

OPENCLAW_CLI = "openclaw"
WORKSPACE_BASE = os.path.expanduser("~/.openclaw")

# 预设团队模板
ROLE_DEFAULT_MODELS = {
    "产品": "minimax/MiniMax-M2.5",
    "设计": "minimax/MiniMax-M2.5",
    "开发": "openai-codex/gpt-5.4",
    "测试": "minimax/MiniMax-M2.5",
    "运维": "minimax/MiniMax-M2.5",
    "研究": "openai-codex/gpt-5.4",
    "前端": "openai-codex/gpt-5.4",
    "后端": "openai-codex/gpt-5.4",
}

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "templates")

TEAM_TEMPLATES = {
    "default": {
        "agents": [
            {"name": "pm", "emoji": "📋", "role": "产品"},
            {"name": "ui", "emoji": "🎨", "role": "设计"},
            {"name": "coding", "emoji": "💻", "role": "开发"},
        ]
    },
    "full": {
        "agents": [
            {"name": "pm", "emoji": "📋", "role": "产品"},
            {"name": "ui", "emoji": "🎨", "role": "设计"},
            {"name": "coding", "emoji": "💻", "role": "开发"},
            {"name": "tester", "emoji": "🧪", "role": "测试"},
            {"name": "devops", "emoji": "🔧", "role": "运维"},
        ]
    },
    "minimal": {
        "agents": [
            {"name": "pm", "emoji": "📋", "role": "产品"},
            {"name": "coding", "emoji": "💻", "role": "开发"},
        ]
    },
    "ai": {
        "agents": [
            {"name": "pm", "emoji": "📋", "role": "产品"},
            {"name": "coding", "emoji": "💻", "role": "开发"},
            {"name": "researcher", "emoji": "🔬", "role": "研究"},
        ]
    },
    "web": {
        "agents": [
            {"name": "frontend", "emoji": "🌐", "role": "前端"},
            {"name": "backend", "emoji": "⚙️", "role": "后端"},
            {"name": "designer", "emoji": "✨", "role": "设计"},
        ]
    },
}

def run_cmd(cmd):
    """执行命令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def resolve_model(spec, fallback_model, smart_model=False):
    if spec.get("model"):
        return spec["model"]
    if smart_model and spec.get("role") in ROLE_DEFAULT_MODELS:
        return ROLE_DEFAULT_MODELS[spec["role"]]
    return fallback_model


def create_agent(agent_name, model=None, bind_feishu=False, workspace_base=None, dry_run=False, skip_existing=False, emoji_override=None, role_override=None, init_files=False):
    """创建单个 agent"""
    base = workspace_base or WORKSPACE_BASE
    workspace = f"{base}/workspace-{agent_name}"
    
    print(f"\n📦 {agent_name}")
    print(f"   📁 workspace: {workspace}")

    if dry_run:
        print(f"   👀 dry-run: 将创建 agent（模型: {model or '默认'}）")
        if bind_feishu:
            print(f"   👀 dry-run: 将绑定飞书 bot_{agent_name}")
        return True

    # 1. 创建 agent
    cmd = f"{OPENCLAW_CLI} agents add {agent_name} --workspace {workspace} --non-interactive"
    if model:
        cmd += f" --model {model}"
    
    success, stdout, stderr = run_cmd(cmd)
    if not success:
        err = (stderr or stdout).strip()
        if skip_existing and ("already exists" in err.lower() or "duplicate" in err.lower()):
            print("   ⏭️ 已存在，跳过创建")
        else:
            print(f"   ❌ 创建失败: {err[:120]}")
            return False
    else:
        print(f"   ✅ 已创建")
    
    # 2. 创建 identity 文件
    identity_path = f"{workspace}/IDENTITY.md"
    try:
        os.makedirs(workspace, exist_ok=True)
        emoji = {"pm": "📋", "ui": "🎨", "coding": "💻", "tester": "🧪", 
                 "devops": "🔧", "researcher": "🔬", "frontend": "🌐", 
                 "backend": "⚙️", "designer": "✨"}
        icon = emoji_override or emoji.get(agent_name, "🤖")
        role_text = role_override or "AI Assistant"
        
        identity_content = f"""# IDENTITY.md - {agent_name.title()}

- **Name:** {agent_name}
- **Emoji:** {icon}
- **Identity:** {role_text}
"""
        with open(identity_path, 'w') as f:
            f.write(identity_content)
        print(f"   ✅ identity 已设置")

        if init_files:
            soul_path = f"{workspace}/SOUL.md"
            agents_path = f"{workspace}/AGENTS.md"
            user_path = f"{workspace}/USER.md"
            if not os.path.exists(soul_path):
                with open(soul_path, 'w') as f:
                    f.write(f"# SOUL.md\n\n你是 {agent_name}，角色是{role_text}。保持专业、直接、可信。\n")
            if not os.path.exists(agents_path):
                with open(agents_path, 'w') as f:
                    f.write(f"# AGENTS.md\n\n- {agent_name}: {role_text}\n")
            if not os.path.exists(user_path):
                with open(user_path, 'w') as f:
                    f.write("# USER.md\n\n- Name: 用户\n")
            print(f"   ✅ 初始化 bootstrap 文件")
    except Exception as e:
        print(f"   ⚠️ identity 设置失败: {e}")
    
    # 3. 绑定飞书
    if bind_feishu:
        bot_name = f"bot_{agent_name}"
        cmd = f"{OPENCLAW_CLI} agents bind --agent {agent_name} --bind feishu"
        success, stdout, stderr = run_cmd(cmd)
        if success:
            print(f"   ✅ 飞书绑定: {bot_name}")
        else:
            err = stderr.strip()
            if "already present" in err.lower():
                print(f"   ✅ 飞书绑定: {bot_name} (已存在)")
            else:
                print(f"   ⚠️ 飞书绑定: {bot_name} (需配置)")
    
    return True

def load_team_file(path):
    """从 JSON/YAML 文件加载团队配置"""
    ext = os.path.splitext(path)[1].lower()
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    if ext == '.json':
        data = json.loads(raw)
    elif ext in ('.yml', '.yaml'):
        try:
            import yaml
        except ImportError:
            raise ValueError("读取 YAML 需要安装 pyyaml：pip install pyyaml")
        data = yaml.safe_load(raw)
    else:
        raise ValueError("团队配置文件仅支持 .json / .yml / .yaml")
    if isinstance(data, dict) and "agents" in data:
        return data
    raise ValueError("团队配置文件必须是形如 {\"agents\": [...]} 的对象")


def export_team_config(path, team_name, agent_specs, default_model):
    """导出团队配置为 JSON"""
    payload = {
        "name": team_name,
        "agents": []
    }
    for spec in agent_specs:
        payload["agents"].append({
            "name": spec["name"],
            "emoji": spec.get("emoji", "🤖"),
            "role": spec.get("role", "AI Assistant"),
            "model": spec.get("model", default_model),
        })
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def build_bot_skeleton(agent_specs):
    """生成 bot 配置骨架"""
    skeleton = {}
    for spec in agent_specs:
        name = spec["name"]
        skeleton[f"bot_{name}"] = {
            "appId": f"cli_your_{name}_app_id",
            "appSecret": f"your_{name}_app_secret",
            "botName": f"bot_{name}"
        }
    return skeleton


def build_next_steps(agent_names, effective_bind_feishu=False, exported_patch=None, exported_bot_skeleton=None):
    steps = []
    if exported_bot_skeleton:
        steps.append(f"补全 bot 配置骨架文件中的 appId / appSecret: {exported_bot_skeleton}")
    if exported_patch:
        steps.append(f"检查并应用 config.patch 文件: {exported_patch}")
    if effective_bind_feishu:
        for name in agent_names:
            steps.append(f"在飞书开放平台创建/发布 bot_{name} 对应应用")
            steps.append(f"将 bot_{name} 拉入目标群")
    steps.append("如修改了 OpenClaw 配置，执行: openclaw gateway restart")
    steps.append("执行 openclaw agents list 检查 agent 是否已创建")
    return steps


def build_summary(team_name, agent_specs, effective_bind_feishu, exported_files=None, next_steps=None, validation=None, smart_model=False):
    return {
        "team": team_name,
        "agent_count": len(agent_specs),
        "agents": [
            {
                "name": spec["name"],
                "role": spec.get("role"),
                "emoji": spec.get("emoji"),
                "model": spec.get("resolved_model") or spec.get("model"),
            }
            for spec in agent_specs
        ],
        "bind_feishu": effective_bind_feishu,
        "smart_model": smart_model,
        "exported_files": exported_files or {},
        "validation": validation,
        "next_steps": next_steps or [],
    }


def print_summary(summary):
    print("\n📊 结构化摘要:")
    print(f"   团队: {summary['team']}")
    print(f"   Agent 数量: {summary['agent_count']}")
    print(f"   飞书绑定: {summary['bind_feishu']}")
    print(f"   智能模型: {summary['smart_model']}")
    for agent in summary['agents']:
        print(f"   - {agent['name']} ({agent.get('role') or '未指定'}) → {agent.get('model')}")


def validate_created_team(agent_names, workspace_base=None):
    """校验团队创建结果"""
    base = workspace_base or WORKSPACE_BASE
    results = []
    ok, stdout, stderr = run_cmd(f"{OPENCLAW_CLI} agents list")
    agent_list_text = stdout if ok else ""
    for name in agent_names:
        workspace = f"{base}/workspace-{name}"
        exists_in_list = name in agent_list_text
        workspace_exists = os.path.isdir(workspace)
        identity_exists = os.path.isfile(os.path.join(workspace, "IDENTITY.md"))
        results.append({
            "name": name,
            "listed": exists_in_list,
            "workspace": workspace_exists,
            "identity": identity_exists,
        })
    return results


def build_openclaw_config_patch(agent_specs, bot_prefix=None, include_bindings=False):
    """生成可用于 openclaw config.patch 的 bot accounts 配置骨架"""
    accounts = {}
    bindings = []
    for spec in agent_specs:
        name = spec["name"]
        bot_name = f"bot_{bot_prefix}_{name}" if bot_prefix else f"bot_{name}"
        accounts[bot_name] = {
            "appId": f"cli_your_{name}_app_id",
            "appSecret": f"your_{name}_app_secret",
            "botName": bot_name,
        }
        if include_bindings:
            bindings.append({
                "agentId": name,
                "match": {
                    "channel": "feishu",
                    "accountId": bot_name,
                }
            })
    patch = {
        "channels": {
            "feishu": {
                "accounts": accounts
            }
        }
    }
    if include_bindings:
        patch["bindings"] = bindings
    return patch


def clone_existing_team(agent_names):
    """基于现有 agent 名称生成团队配置"""
    emoji_map = {"pm": "📋", "ui": "🎨", "coding": "💻", "tester": "🧪",
                 "devops": "🔧", "researcher": "🔬", "frontend": "🌐",
                 "backend": "⚙️", "designer": "✨"}
    role_map = {"pm": "产品", "ui": "设计", "coding": "开发", "tester": "测试",
                "devops": "运维", "researcher": "研究", "frontend": "前端",
                "backend": "后端", "designer": "设计"}
    return {
        "name": "cloned-team",
        "agents": [
            {
                "name": name,
                "emoji": emoji_map.get(name, "🤖"),
                "role": role_map.get(name, "AI Assistant")
            }
            for name in agent_names
        ]
    }


def merge_agent_specs(base_agents, child_agents):
    """按 name 合并 agent 配置；子模板可覆盖字段，也可新增 agent"""
    merged = {a["name"]: dict(a) for a in base_agents}
    order = [a["name"] for a in base_agents]
    for agent in child_agents:
        name = agent["name"]
        if name in merged:
            merged[name].update(agent)
        else:
            merged[name] = dict(agent)
            order.append(name)
    return [merged[name] for name in order]


def load_template_file(name):
    """从 assets/templates 加载模板（支持继承）"""
    for ext in (".json", ".yaml", ".yml"):
        path = os.path.join(TEMPLATE_DIR, name + ext)
        if os.path.exists(path):
            data = load_team_file(path)
            parent = data.get("extends")
            if parent:
                base = load_template_file(parent)
                merged_agents = merge_agent_specs(base.get("agents", []), data.get("agents", []))
                data = {**base, **data, "agents": merged_agents}
            return data
    raise FileNotFoundError(f"模板不存在: {name}")


def show_templates():
    """显示可用模板"""
    print("\n📋 可用模板:")
    print("-" * 40)
    for name, template in TEAM_TEMPLATES.items():
        agents = [a["name"] for a in template["agents"]]
        print(f"  {name:12} → {', '.join(agents)}")
    if os.path.isdir(TEMPLATE_DIR):
        for filename in sorted(os.listdir(TEMPLATE_DIR)):
            if filename.endswith((".json", ".yaml", ".yml")):
                tpl_name = os.path.splitext(filename)[0]
                try:
                    tpl = load_template_file(tpl_name)
                    desc = tpl.get("description", "file template")
                    print(f"  {tpl_name:12} → {desc}")
                except Exception:
                    print(f"  {tpl_name:12} → (file template)")
    print("-" * 40)

def main():
    parser = argparse.ArgumentParser(description="Agent 团队创建器")
    parser.add_argument("--template", "-t", help="团队模板: " + ", ".join(TEAM_TEMPLATES.keys()))
    parser.add_argument("--agents", "-a", help="自定义 agent 列表（逗号分隔）")
    parser.add_argument("--model", "-m", default="minimax/MiniMax-M2.5", help="模型")
    parser.add_argument("--bind-feishu", "-f", action="store_true", help="绑定飞书")
    parser.add_argument("--no-bind-feishu", action="store_true", help="即使模板建议绑定，也不绑定飞书")
    parser.add_argument("--workspace-base", "-w", help="workspace 根目录")
    parser.add_argument("--list", "-l", action="store_true", help="显示可用模板")
    parser.add_argument("--describe-template", help="显示模板详情")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不实际创建")
    parser.add_argument("--skip-existing", action="store_true", help="已存在则跳过")
    parser.add_argument("--team-file", help="从 JSON 文件加载团队配置")
    parser.add_argument("--export-team-file", help="将当前团队配置导出为 JSON 文件")
    parser.add_argument("--clone-agents", help="基于现有 agent 名称克隆团队配置，如 pm,ui,coding")
    parser.add_argument("--export-bot-skeleton", help="导出飞书 bot 配置骨架 JSON")
    parser.add_argument("--export-config-patch", help="导出 OpenClaw config.patch 骨架 JSON")
    parser.add_argument("--bot-prefix", help="生成 bot 名称前缀，如 team1")
    parser.add_argument("--include-bindings", action="store_true", help="导出的 patch 中包含 agent 绑定")
    parser.add_argument("--validate", action="store_true", help="创建后执行校验")
    parser.add_argument("--smart-model", action="store_true", help="按角色自动选择默认模型")
    parser.add_argument("--init-files", action="store_true", help="初始化 SOUL.md / AGENTS.md / USER.md")
    parser.add_argument("--summary", action="store_true", help="输出结构化摘要")
    parser.add_argument("--report-file", help="将结构化摘要写入 JSON 文件")
    
    args = parser.parse_args()
    
    # 显示模板列表
    if args.list:
        show_templates()
        return

    if args.describe_template:
        name = args.describe_template
        if name in TEAM_TEMPLATES:
            tpl = TEAM_TEMPLATES[name]
        else:
            tpl = load_template_file(name)
        print(json.dumps(tpl, ensure_ascii=False, indent=2))
        return
    
    # 获取 agent 列表
    template_meta = {}
    if args.clone_agents:
        cloned = clone_existing_team([a.strip() for a in args.clone_agents.split(",") if a.strip()])
        agent_specs = cloned["agents"]
        team_name = cloned.get("name", "cloned-team")
        template_meta = cloned
    elif args.team_file:
        team = load_team_file(args.team_file)
        agent_specs = team["agents"]
        team_name = team.get("name", "file")
        template_meta = team
    elif args.template:
        if args.template in TEAM_TEMPLATES:
            template = TEAM_TEMPLATES[args.template]
        else:
            try:
                template = load_template_file(args.template)
            except Exception:
                print(f"❌ 未知模板: {args.template}")
                show_templates()
                sys.exit(1)
        agent_specs = template["agents"]
        team_name = template.get("name", args.template)
        template_meta = template
    elif args.agents:
        agent_specs = [{"name": a.strip()} for a in args.agents.split(",") if a.strip()]
        team_name = "custom"
    else:
        print("❌ 请指定 --template 或 --agents")
        print("\n用法:")
        print("  python team_creator.py --template default")
        print("  python team_creator.py --agents pm,ui,coding")
        print("\n可用模板:")
        show_templates()
        sys.exit(1)
    
    if not agent_specs:
        print("❌ agent 列表为空")
        sys.exit(1)

    agent_names = [a["name"] for a in agent_specs]

    effective_bind_feishu = args.bind_feishu
    if not args.bind_feishu and not args.no_bind_feishu and template_meta.get("default_bind_feishu") is True:
        effective_bind_feishu = True

    if args.export_team_file:
        export_team_config(args.export_team_file, team_name, agent_specs, args.model)
        print(f"✅ 已导出团队配置: {args.export_team_file}")
        summary = build_summary(team_name, agent_specs, effective_bind_feishu, exported_files={"team_file": args.export_team_file})
        if args.summary:
            print_summary(summary)
        if args.report_file:
            with open(args.report_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
        return

    if args.export_bot_skeleton:
        skeleton = build_bot_skeleton(agent_specs)
        with open(args.export_bot_skeleton, 'w', encoding='utf-8') as f:
            json.dump(skeleton, f, ensure_ascii=False, indent=2)
        print(f"✅ 已导出 bot 配置骨架: {args.export_bot_skeleton}")
        next_steps = build_next_steps(agent_names, effective_bind_feishu, exported_bot_skeleton=args.export_bot_skeleton)
        print("\n📌 下一步建议:")
        for step in next_steps:
            print(f"   - {step}")
        summary = build_summary(team_name, agent_specs, effective_bind_feishu, exported_files={"bot_skeleton": args.export_bot_skeleton}, next_steps=next_steps)
        if args.summary:
            print_summary(summary)
        if args.report_file:
            with open(args.report_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
        return

    if args.export_config_patch:
        patch = build_openclaw_config_patch(
            agent_specs,
            bot_prefix=args.bot_prefix,
            include_bindings=args.include_bindings,
        )
        with open(args.export_config_patch, 'w', encoding='utf-8') as f:
            json.dump(patch, f, ensure_ascii=False, indent=2)
        print(f"✅ 已导出 OpenClaw config.patch 骨架: {args.export_config_patch}")
        next_steps = build_next_steps(agent_names, effective_bind_feishu, exported_patch=args.export_config_patch)
        print("\n📌 下一步建议:")
        for step in next_steps:
            print(f"   - {step}")
        summary = build_summary(team_name, agent_specs, effective_bind_feishu, exported_files={"config_patch": args.export_config_patch}, next_steps=next_steps)
        if args.summary:
            print_summary(summary)
        if args.report_file:
            with open(args.report_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
        return
    
    # 执行创建
    print("=" * 50)
    print(f"🚀 正在创建团队: {team_name} ({', '.join(agent_names)})")
    print(f"   model: {args.model}")
    print(f"   bind-feishu: {effective_bind_feishu}")
    print("=" * 50)
    
    success_count = 0
    for spec in agent_specs:
        agent_model = resolve_model(spec, args.model, args.smart_model)
        spec["resolved_model"] = agent_model
        if create_agent(
            spec["name"],
            agent_model,
            effective_bind_feishu,
            workspace_base=args.workspace_base,
            dry_run=args.dry_run,
            skip_existing=args.skip_existing,
            emoji_override=spec.get("emoji"),
            role_override=spec.get("role"),
            init_files=args.init_files,
        ):
            success_count += 1
    
    print("\n" + "=" * 50)
    if success_count == len(agent_specs):
        print(f"🎉 团队创建完成! ({success_count}/{len(agent_specs)})")
    else:
        print(f"⚠️ 部分完成 ({success_count}/{len(agent_specs)})")
    
    validation = None
    if args.validate:
        validation = validate_created_team(agent_names, args.workspace_base)
        print("\n🔎 校验结果:")
        for item in validation:
            status = "✅" if item["listed"] and item["workspace"] and item["identity"] else "⚠️"
            print(f"   {status} {item['name']}: listed={item['listed']} workspace={item['workspace']} identity={item['identity']}")

    next_steps = build_next_steps(agent_names, effective_bind_feishu)
    print("\n📌 下一步建议:")
    for step in next_steps:
        print(f"   - {step}")

    summary = build_summary(team_name, agent_specs, effective_bind_feishu, next_steps=next_steps, validation=validation, smart_model=args.smart_model)
    if args.summary:
        print_summary(summary)
    if args.report_file:
        with open(args.report_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    print("=" * 50)

if __name__ == "__main__":
    main()
