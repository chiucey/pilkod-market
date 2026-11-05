# liye-analyzer — 安装与使用说明

## 这是什么

Linux 系统层深度排障分析 skill，专精：
- sosreport 诊断
- 国产化生态：麒麟（高级服务器/桌面）、UOS、openEuler、CentOS、RHEL、Ubuntu
- 国产芯片：鲲鹏（ARM）、海光（x86）、飞腾（ARM）、龙芯
- KVM 虚拟化
- 应用层 system-side：Java/Python/Go 进程 OOM、fd 耗尽、cgroup 限制

## 文件清单

```
liye-analyzer/
├── SKILL.md                    # 主文件：触发规则 + 执行流程
├── INSTALL.md                  # 本文件
└── references/
    ├── distro-paths.md         # 各发行版关键路径速查
    ├── chip-checklist.md       # 国产芯片检查清单
    ├── kvm-checklist.md        # KVM 排障清单
    ├── desktop-checklist.md    # 桌面问题清单
    └── output-template.md      # 报告章节模板
```

## 安装方法

### 方法 A：放入 Mavis skills 同步目录（推荐）

```bash
# 解压到 Mavis 的 skills 同步目录
mkdir -p ~/.mavis/skills/
tar xzf liye-analyzer.tar.gz -C ~/.mavis/skills/
# 或 unzip
unzip liye-analyzer.zip -d ~/.mavis/skills/

# 重启 Mavis 客户端 / 刷新技能列表
```

### 方法 B：放入项目的 `.skills/` 目录

```bash
# 在你的工作项目根目录
mkdir -p .skills/
tar xzf liye-analyzer.tar.gz -C .skills/
```

## 触发条件

在 Mavis 客户端里这样说会触发 liye-analyzer：

- "分析这个 sosreport"
- "麒麟服务器宕机了，帮我看看"
- "生成一份运维分析报告"
- "服务器频繁重启，帮我定位"
- 上传 sosreport 压缩包 + 任何主诉

## 输出

- `findings.md`（结构化中间产物）
- `report.docx`（正式 Word 报告，17 页样式参考）

报告章节固定：概览 / 系统信息 / 资源分析 / 异常时间线 / 根因结论 / 优化建议 / 附录。

## 首次使用建议

1. 准备一个脱敏后的真实 sosreport（建议先小测试：< 50MB 的简单场景）
2. 主诉清楚点（"宕机"/"性能慢"/"IO 异常"等）
3. 看 `findings.md` 了解分析逻辑
4. 用 `report.docx` 给现场运维团队

## 不适用场景

- 纯业务代码 bug（Java 单元测试失败、SQL 调优）
- 纯前端/浏览器问题
- 软件安装/服务配置的操作手册
- 纯安全合规审计

## 版本

v1.0 — 2026-08-04

基于真实 GaussDB on Kunpeng 920 + Kylin V10 + MegaRAID 9460-8i 案例迭代生成。

## 反馈与迭代

跑完一个真实案例后，反馈给我：
- 哪些 references 真正用到了？哪些没用？
- 触发的描述（description）准不准？
- Procedure 步骤有没有缺/多/绕路？
- 报告样式是否合用？

下个版本会基于实际使用反馈迭代。
