# use-wisely v1.3.0

MiniMax M2.7 / Agent Skills compatible 默认总调度技能。

## 本版修复

- 重新用标准 zip 打包，单一根目录：`use-wisely/`。
- 增加 zip 自检：`python scripts/quick_validate.py /path/to/use-wisely-v1.3-final.zip`。
- 强化编程任务：精简、可运行、可验证。
- 强化情感任务：细致共情、记住称呼、温柔告别、危机电话和局限性。
- 增加技能目录扫描预览脚本：`scripts/skill_scan_preview.py`。

## 指定技能目录

```bash
export USE_WISELY_SKILL_DIRS="/path/to/user/skills:/path/to/system/skills"
```

或直接在对话中指定目录。

## 验证

```bash
python scripts/quick_validate.py .
python scripts/quick_validate.py ../use-wisely-v1.3-final.zip
```

## 说明

本技能不能绕过宿主平台权限，也不能保证平台 100% 每次自动调用；它通过 `description`、安装位置和默认技能配置尽量实现 `use widely`。
