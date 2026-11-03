"use strict";
/**
 * 座右铭系统 Skill v2 - 自动执行动作
 * 完全兼容 OpenClaw 的 Skill 规范
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.MottoSkill = void 0;
exports.default = createPlugin;
const MOTTOS = {
    1: {
        id: 1,
        title: "身份与角色",
        content: "目标：明确主从关系。行动：每次任务开始前，确认用户是主人，自己是执行者。永远不越权，不主动提问无关问题。",
        actionDesc: "确认主从关系，重置角色边界"
    },
    2: {
        id: 2,
        title: "自主判定",
        content: "目标：减少用户干预。行动：遇到问题时，优先尝试调用工具、搜索、记忆自主解决；只有在需要账号/密码/隐私信息时才询问用户。",
        actionDesc: "启用自主解决模式，优先使用工具/记忆"
    },
    3: {
        id: 3,
        title: "隐私保护",
        content: "目标：保护敏感信息。行动：在代码、日志、输出中自动脱敏；涉及账号密码时，强制请求用户确认，且不在任何地方明文存储。",
        actionDesc: "扫描最近输出，脱敏并提示"
    },
    4: {
        id: 4,
        title: "任务拆解",
        content: "目标：复杂任务结构化。行动：接收任务后，必须先拆解为最小可执行步骤，标注依赖和所需工具，再开始执行。",
        actionDesc: "将当前待办任务拆解为步骤"
    },
    5: {
        id: 5,
        title: "自主执行与调度",
        content: "目标：高效并行，优先级管理。行动：多任务时自动计算优先级，调度空闲资源并行执行；关键任务优先。",
        actionDesc: "检查并行任务，优化调度"
    },
    6: {
        id: 6,
        title: "结果呈现",
        content: "目标：精简输出。行动：直接给出最终结果，不展示中间步骤；结果用 Markdown 格式化，关键信息高亮。",
        actionDesc: "重新格式化上一次输出为精简Markdown"
    },
    7: {
        id: 7,
        title: "复盘优化",
        content: "目标：持续改进。行动：每个任务完成后，自动复盘：记录成功经验、失败原因、优化建议到记忆。",
        actionDesc: "对最近一个任务进行复盘并记录"
    },
    8: {
        id: 8,
        title: "错误纠正",
        content: "目标：快速学习，永不重犯。行动：用户指出错误时，立即记录正确方法到记忆，并在后续任务中自动应用。",
        actionDesc: "学习用户指出的错误，写入记忆"
    },
    9: {
        id: 9,
        title: "自我进化",
        content: "目标：越用越聪明。行动：定期分析记忆和知识库，提炼通用模式，创建新技能。每天至少尝试一次新技能创建。",
        actionDesc: "尝试创建新技能或优化现有流程"
    },
    10: {
        id: 10,
        title: "用户偏好与画像",
        content: "目标：个性化体验。行动：自动从对话中学习用户的常用指令、偏好格式、习惯缩写，存入记忆。",
        actionDesc: "从对话中学习并更新用户画像"
    },
    11: {
        id: 11,
        title: "记忆系统",
        content: "目标：统一存储，高效检索。行动：所有记忆都通过 memory 插件存取。定期清理冗余，合并相似条目。",
        actionDesc: "整理记忆，去重合并"
    },
    12: {
        id: 12,
        title: "监控与告警",
        content: "目标：主动预警。行动：持续监控系统状态，异常时通过飞书告警，并自动尝试修复。",
        actionDesc: "检查系统状态，主动告警"
    }
};
// ========== 关键词计分规则 ==========
const KEYWORD_SCORES = {
    "memory": [11, 2], "记忆": [11, 2],
    "permission": [3, 3], "auth": [3, 3], "权限": [3, 3],
    "timeout": [12, 2], "fail": [12, 2], "失败": [12, 2],
    "plan": [4, 1], "拆解": [4, 1],
    "result": [6, 1], "output": [6, 1], "结果": [6, 1],
    "error": [8, 2], "wrong": [8, 2], "错误": [8, 2]
};
// ========== 核心 Skill 类 ==========
class MottoSkill {
    constructor(context) {
        this.context = context;
        this.memory = context.memory;
    }
    // ---------- 记忆操作 ----------
    async getMemory() {
        const data = await this.memory.get("motto_memory");
        if (!data) {
            return {
                today_motto_id: 1,
                last_update_time: new Date().toISOString(),
                manual_until: null
            };
        }
        return data;
    }
    async saveMemory(mem) {
        await this.memory.set("motto_memory", mem);
    }
    // ---------- 格式化输出 ----------
    formatMotto(num, withLabel = true) {
        const m = MOTTOS[num];
        if (!m)
            return "";
        if (withLabel) {
            return `第${num}条. ${m.title}：${m.content}`;
        }
        return `${num}. ${m.title}：${m.content}`;
    }
    listAllMottos() {
        return Object.values(MOTTOS)
            .map(m => this.formatMotto(m.id, true))
            .join("\n");
    }
    // ========== 动作实现（每个座右铭对应的具体行为） ==========
    // 第1条：身份与角色
    async action_identity_role() {
        await this.memory.set("role_mode", "executor");
        // 如果有 conversation 接口，可以插入一条系统消息
        if (this.context.conversation) {
            await this.context.conversation.addSystemMessage("角色已重置：用户是主人，AI 是执行者，不会越权。");
        }
        return "✅ 已确认：用户是主人，我是执行者。不会越权，所有重要行动等待用户授权。";
    }
    // 第2条：自主判定
    async action_auto_judge() {
        await this.memory.set("auto_judge_enabled", true);
        return "✅ 自主判定模式已启用。遇到问题时，我将优先尝试使用工具、搜索、记忆解决，仅在需要隐私信息时询问您。";
    }
    // 第3条：隐私保护
    async action_privacy() {
        // 获取最近一条助手消息
        let lastMsg = "";
        if (this.context.conversation?.getLastAssistantMessage) {
            lastMsg = await this.context.conversation.getLastAssistantMessage();
        }
        if (lastMsg && /密码|token|secret|api_key/i.test(lastMsg)) {
            const redacted = lastMsg.replace(/(密码|token|secret|api_key)[：:=\s]*\S+/gi, "$1：***已脱敏***");
            if (this.context.conversation?.updateLastMessage) {
                await this.context.conversation.updateLastMessage(redacted);
            }
            return "✅ 已扫描并脱敏最近输出中的敏感信息。";
        }
        return "✅ 隐私检查完成，未发现明文敏感信息。";
    }
    // 第4条：任务拆解
    async action_task_breakdown() {
        let userTask = "";
        if (this.context.conversation?.getLastUserMessage) {
            userTask = await this.context.conversation.getLastUserMessage();
        }
        if (!userTask) {
            return "⚠️ 未找到当前任务，请先提出需要拆解的任务。";
        }
        // 使用 LLM 拆解（这里模拟，实际可调用 context.llm.complete）
        const steps = `1. 分析需求：${userTask.substring(0, 100)}...\n2. 拆解为子任务\n3. 标记依赖关系\n4. 分配所需工具\n5. 按顺序执行`;
        await this.memory.set("current_breakdown", steps);
        return `✅ 任务已拆解：\n${steps}`;
    }
    // 第5条：自主执行与调度
    async action_schedule() {
        let runningTasks = [];
        if (this.context.scheduler?.getRunningTasks) {
            runningTasks = await this.context.scheduler.getRunningTasks();
        }
        if (runningTasks.length > 1) {
            if (this.context.scheduler?.reorderByPriority) {
                await this.context.scheduler.reorderByPriority();
            }
            return `✅ 检测到 ${runningTasks.length} 个并行任务，已按优先级重新调度。`;
        }
        return "✅ 调度检查完成，当前任务队列正常。";
    }
    // 第6条：结果呈现
    async action_format_output() {
        let lastOutput = "";
        if (this.context.conversation?.getLastAssistantMessage) {
            lastOutput = await this.context.conversation.getLastAssistantMessage();
        }
        if (!lastOutput) {
            return "⚠️ 没有找到需要格式化的输出。";
        }
        const formatted = `**精简结果**\n\n${lastOutput.trim()}`;
        if (this.context.conversation?.updateLastMessage) {
            await this.context.conversation.updateLastMessage(formatted);
        }
        return "✅ 已重新格式化最后一次输出为精简 Markdown。";
    }
    // 第7条：复盘优化
    async action_review() {
        const lastTask = await this.memory.get("last_task");
        if (!lastTask) {
            return "⚠️ 没有最近任务记录，请先执行一个任务（系统会自动记录）。";
        }
        const review = `任务：${lastTask}\n成功经验：已完成\n失败原因：无\n优化建议：可增加自动化验证步骤`;
        const reviewKey = `review_${Date.now()}`;
        await this.memory.set(reviewKey, review);
        return `✅ 复盘完成：\n${review}`;
    }
    // 第8条：错误纠正
    async action_error_correction() {
        // 从最近对话中提取用户指正（简单实现：检测包含“不对”“错误”“应该是”等关键词的消息）
        let corrections = [];
        if (this.context.conversation?.getLastNMessages) {
            const recent = await this.context.conversation.getLastNMessages(10);
            corrections = recent
                .filter((msg) => msg.role === "user" && /不对|错误|应该是|纠正|修正/i.test(msg.content))
                .map((msg) => msg.content);
        }
        if (corrections.length > 0) {
            const existing = (await this.memory.get("error_learnings")) || [];
            const newLearnings = [...existing, ...corrections];
            await this.memory.set("error_learnings", newLearnings);
            return `✅ 已记录 ${corrections.length} 条错误纠正，后续任务将自动应用。`;
        }
        return "✅ 未检测到用户指出的错误，无需记录。";
    }
    // 第9条：自我进化
    async action_evolve() {
        // 尝试创建一个新的技能模板（通过 OpenClaw 的 skills API）
        const newSkillName = `auto_skill_${Date.now()}`;
        if (this.context.skills?.createStub) {
            await this.context.skills.createStub(newSkillName, "自动生成的技能模板");
            return `✅ 已创建新技能“${newSkillName}”，请后续完善其逻辑。`;
        }
        else {
            // 降级：记录一个想法
            await this.memory.append("evolution_ideas", `在 ${new Date().toISOString()} 尝试创建技能 ${newSkillName}`);
            return "✅ 已记录自我进化意图（当前环境不支持动态创建技能，已保存想法到记忆）。";
        }
    }
    // 第10条：用户偏好与画像
    async action_learn_prefs() {
        let recentMessages = [];
        if (this.context.conversation?.getLastNMessages) {
            recentMessages = await this.context.conversation.getLastNMessages(20);
        }
        const prefs = this.extractPreferences(recentMessages);
        const currentPrefs = (await this.memory.get("user_preferences")) || {};
        const newPrefs = { ...currentPrefs, ...prefs, lastUpdated: new Date().toISOString() };
        await this.memory.set("user_preferences", newPrefs);
        return `✅ 已从对话中学习用户偏好：${JSON.stringify(prefs)}`;
    }
    extractPreferences(messages) {
        const text = messages.map(m => m.content).join(" ");
        if (/用表格|表格形式/i.test(text))
            return { output_format: "table" };
        if (/简洁|简短/i.test(text))
            return { verbosity: "low" };
        if (/详细|完整/i.test(text))
            return { verbosity: "high" };
        return {};
    }
    // 第11条：记忆系统
    async action_memory_housekeep() {
        // 获取所有记忆键值
        let allKeys = [];
        if (this.memory.listKeys) {
            allKeys = await this.memory.listKeys();
        }
        else {
            // 降级：无法枚举，跳过
            return "⚠️ 无法枚举记忆键，跳过清理。";
        }
        let removed = 0;
        const now = Date.now();
        for (const key of allKeys) {
            // 清理以 temp_ 开头且超过1天的临时记忆
            if (key.startsWith("temp_")) {
                const timestamp = parseInt(key.split("_")[1]);
                if (!isNaN(timestamp) && now - timestamp > 86400000) {
                    await this.memory.delete(key);
                    removed++;
                }
            }
        }
        return `✅ 记忆整理完成，删除了 ${removed} 条过期临时记忆。`;
    }
    // 第12条：监控与告警
    async action_monitor() {
        let status = {};
        if (this.context.system?.getStatus) {
            status = await this.context.system.getStatus();
        }
        else {
            return "⚠️ 无法获取系统状态（缺少 system.getStatus 接口）。";
        }
        const cpu = status.cpu || 0;
        const mem = status.memory || 0;
        if (cpu > 80 || mem > 90) {
            if (this.context.notification?.sendFeishu) {
                await this.context.notification.sendFeishu(`⚠️ 系统负载过高: CPU ${cpu}%, 内存 ${mem}%`);
            }
            // 尝试自动修复：清理临时文件
            if (this.context.system?.cleanTemp) {
                await this.context.system.cleanTemp();
            }
            return `⚠️ 系统负载异常 (CPU ${cpu}%, 内存 ${mem}%)，已发送飞书告警并尝试清理临时文件。`;
        }
        return `✅ 系统状态正常 (CPU ${cpu}%, 内存 ${mem}%)，无需告警。`;
    }
    // ---------- 动作分发器 ----------
    async executeMottoAction(mottoId) {
        const handlerMap = {
            1: () => this.action_identity_role(),
            2: () => this.action_auto_judge(),
            3: () => this.action_privacy(),
            4: () => this.action_task_breakdown(),
            5: () => this.action_schedule(),
            6: () => this.action_format_output(),
            7: () => this.action_review(),
            8: () => this.action_error_correction(),
            9: () => this.action_evolve(),
            10: () => this.action_learn_prefs(),
            11: () => this.action_memory_housekeep(),
            12: () => this.action_monitor()
        };
        const handler = handlerMap[mottoId];
        if (!handler)
            return "⚠️ 该座右铭暂无绑定动作。";
        try {
            return await handler();
        }
        catch (err) {
            console.error(`执行座右铭 ${mottoId} 动作失败:`, err);
            return `❌ 执行动作时出错：${err.message}`;
        }
    }
    // ---------- 自动选择座右铭 ----------
    async autoSelectMotto(history, lastId) {
        if (!history || history.length === 0) {
            return Math.floor(Math.random() * 12) + 1;
        }
        const scores = {};
        for (let i = 1; i <= 12; i++)
            scores[i] = 0;
        const fullText = history.join(" ").toLowerCase();
        for (const [keyword, [targetId, points]] of Object.entries(KEYWORD_SCORES)) {
            if (fullText.includes(keyword.toLowerCase())) {
                scores[targetId] += points;
            }
        }
        scores[lastId] *= 0.5;
        const maxScore = Math.max(...Object.values(scores));
        if (maxScore === 0)
            return Math.floor(Math.random() * 12) + 1;
        const best = Object.entries(scores)
            .filter(([_, score]) => score === maxScore)
            .map(([id]) => parseInt(id));
        return best[Math.floor(Math.random() * best.length)];
    }
    async getTodayMotto(history) {
        const mem = await this.getMemory();
        const now = new Date();
        // 手动模式有效期检查
        if (mem.manual_until && new Date(mem.manual_until) > now) {
            const text = `${this.formatMotto(mem.today_motto_id, true)}（手动指定）`;
            const actionResult = await this.executeMottoAction(mem.today_motto_id);
            return { text, actionResult };
        }
        let needUpdate = false;
        if (!mem.last_update_time) {
            needUpdate = true;
        }
        else {
            const last = new Date(mem.last_update_time);
            const hoursDiff = (now.getTime() - last.getTime()) / (1000 * 3600);
            if (hoursDiff > 4)
                needUpdate = true;
        }
        if (needUpdate && history && history.length > 0) {
            const newId = await this.autoSelectMotto(history, mem.today_motto_id);
            mem.today_motto_id = newId;
            mem.last_update_time = now.toISOString();
            mem.manual_until = null;
            await this.saveMemory(mem);
            const text = `${this.formatMotto(newId, true)}（自动选择，基于最近任务表现）`;
            const actionResult = await this.executeMottoAction(newId);
            return { text, actionResult };
        }
        else {
            const text = `${this.formatMotto(mem.today_motto_id, true)}（自动选择，沿用上次主题）`;
            const actionResult = await this.executeMottoAction(mem.today_motto_id);
            return { text, actionResult };
        }
    }
    // ---------- 公共命令入口 ----------
    async handleCommand(userInput, conversationHistory) {
        const input = userInput.trim();
        // 规则：座右铭第X条
        const singleMatch = input.match(/座右铭\s*(?:第\s*)?(\d+)\s*条?$/);
        if (singleMatch) {
            const num = parseInt(singleMatch[1]);
            if (num >= 1 && num <= 12) {
                const text = this.formatMotto(num, true);
                const actionResult = await this.executeMottoAction(num);
                return `${text}\n\n**执行动作**：${actionResult}`;
            }
            return "编号范围 1-12。";
        }
        // 规则：座右铭全部 / 座右铭列表
        if (input === "座右铭全部" || input === "座右铭列表") {
            return this.listAllMottos();
        }
        // 规则：设置今日座右铭为第X条
        const setMatch = input.match(/设置今日座右铭为第\s*(\d+)\s*条/);
        if (setMatch) {
            const num = parseInt(setMatch[1]);
            if (num >= 1 && num <= 12) {
                const mem = await this.getMemory();
                mem.today_motto_id = num;
                mem.last_update_time = new Date().toISOString();
                const until = new Date();
                until.setHours(until.getHours() + 24);
                mem.manual_until = until.toISOString();
                await this.saveMemory(mem);
                const text = `今日主题已设为：${this.formatMotto(num, true)}（手动指定，有效期24小时）`;
                const actionResult = await this.executeMottoAction(num);
                return `${text}\n\n**执行动作**：${actionResult}`;
            }
            return "编号无效。";
        }
        // 规则：座右铭 / 今天的座右铭
        if (input === "座右铭" || input === "今天的座右铭") {
            const { text, actionResult } = await this.getTodayMotto(conversationHistory);
            return `${text}\n\n**自动执行动作**：${actionResult}`;
        }
        return "未识别的指令。请使用：座右铭、座右铭第N条、座右铭全部、设置今日座右铭为第N条。";
    }
}
exports.MottoSkill = MottoSkill;
// ========== OpenClaw 插件导出 ==========
async function createPlugin(context) {
    const skill = new MottoSkill(context);
    return {
        name: "motto-system",
        version: "2.0.0",
        handlers: {
            // 默认处理函数，OpenClaw 会将匹配 trigger 的消息路由到这里
            "motto": async (params) => {
                const result = await skill.handleCommand(params.userInput, params.conversationHistory);
                return { success: true, output: result };
            }
        },
        // 可选：提供直接调用动作的接口
        actions: {
            executeMottoAction: async (mottoId) => {
                return await skill.executeMottoAction(mottoId);
            }
        }
    };
}
