#!/usr/bin/env bash
# adversarial-review orchestrate.sh
# 对抗式内容审核编排脚本
# 通过文件读写通信，角色之间互相隔离
#
# 使用方式：
#   1. 在工作目录创建 task-brief.md
#   2. bash ~/.openclaw/skills/adversarial-review/orchestrate.sh
#   3. 产出：final-draft.md + review-summary.md

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${1:-$(pwd)}"
MAX_ROUNDS=3
PASS_SCORE=8

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() { echo -e "${BLUE}[adversarial-review]${NC} $1"; }
ok()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn(){ echo -e "${YELLOW}[⚠]${NC} $1"; }
err() { echo -e "${RED}[✗]${NC} $1"; }

# 检查前置条件
check_prereqs() {
    if [ ! -f "$WORK_DIR/task-brief.md" ]; then
        err "找不到 task-brief.md，请先创建任务简报。"
        echo ""
        echo "任务简报模板："
        echo "  主题：[你的文章主题]"
        echo "  目标读者：[谁会看这篇文章]"
        echo "  核心论点：[这篇文章要说什么观点]"
        echo "  写作风格：[公众号/日记/观点文/演讲稿]"
        echo "  字数要求：[大约多少字]"
        echo "  参考素材：[任何相关的素材、数据、故事]"
        exit 1
    fi

    # 检查 openclaw CLI（用于调用子Agent）
    if ! command -v openclaw &>/dev/null && ! command -v dvcode &>/dev/null; then
        warn "未检测到 openclaw/dvcode CLI，将尝试直接调用 claude"
    fi
}

# 提取裁判分数（从 judgment 文件中解析）
extract_score() {
    local judgment_file="$1"
    if [ ! -f "$judgment_file" ]; then
        echo "0"
        return
    fi
    # 尝试从 "总分：X/10" 格式提取
    local score
    score=$(grep -oP '总分[：:]\s*\K[0-9]+' "$judgment_file" 2>/dev/null | head -1)
    if [ -z "$score" ]; then
        # 备用：从 "**X/10**" 格式提取
        score=$(grep -oP '\*\*\K[0-9]+(?=/10\*\*)' "$judgment_file" 2>/dev/null | head -1)
    fi
    echo "${score:-0}"
}

# 调用写手（笔杆子）
run_writer() {
    local round=$1
    local draft_file="$WORK_DIR/round-${round}-draft.md"
    local prev_critique=""

    if [ "$round" -gt 1 ]; then
        prev_critique="$WORK_DIR/round-$((round-1))-critique.md"
    fi

    log "Round ${round}：笔杆子开始写作..."

    # 构造 prompt
    local writer_prompt
    writer_prompt=$(cat "$SKILL_DIR/writer-prompt.md")

    local task_brief
    task_brief=$(cat "$WORK_DIR/task-brief.md")

    local user_message
    if [ "$round" -eq 1 ]; then
        user_message="请根据以下任务简报写作。这是第${round}轮，请产出完整草稿。

===任务简报===
${task_brief}
=============

请严格按照笔杆子系统提示的风格要求写作，输出完整的文章草稿。"
    else
        local critique_content
        critique_content=$(cat "$prev_critique")
        user_message="这是第${round}轮修改。请根据参谋的挑刺意见，针对性修改上一轮草稿。

===任务简报===
${task_brief}
=============

===上轮草稿===
$(cat "$WORK_DIR/round-$((round-1))-draft.md")
=============

===参谋挑刺===
${critique_content}
=============

请针对性修改，在文章最后附上「修改说明」，说明接受/不接受哪些批评，以及改了什么。"
    fi

    # 调用 claude
    local model="claude-sonnet-4-5"
    if command -v claude &>/dev/null; then
        echo "$user_message" | claude --system "$writer_prompt" --model "$model" > "$draft_file" 2>/dev/null || \
        claude -p "$user_message" --system-prompt "$writer_prompt" > "$draft_file"
    else
        # Fallback: 使用 openclaw subagent
        local combined_prompt="${writer_prompt}

---

${user_message}"
        openclaw run --model "$model" --prompt "$combined_prompt" > "$draft_file"
    fi

    ok "笔杆子完成：$draft_file（$(wc -c < "$draft_file") bytes）"
}

# 调用参谋（挑刺）
run_critic() {
    local round=$1
    local draft_file="$WORK_DIR/round-${round}-draft.md"
    local critique_file="$WORK_DIR/round-${round}-critique.md"

    log "Round ${round}：参谋开始挑刺..."

    local critic_prompt
    critic_prompt=$(cat "$SKILL_DIR/critic-prompt.md")

    local task_brief
    task_brief=$(cat "$WORK_DIR/task-brief.md")

    local draft_content
    draft_content=$(cat "$draft_file")

    local user_message="请对以下文章进行第${round}轮全面挑刺审核。

===任务简报===
${task_brief}
=============

===当前草稿===
${draft_content}
=============

请严格按照参谋挑刺报告格式输出，覆盖全部5个维度，给出综合预判分和必须解决的3件事。"

    local model="claude-sonnet-4-5"
    if command -v claude &>/dev/null; then
        echo "$user_message" | claude --system "$critic_prompt" --model "$model" > "$critique_file" 2>/dev/null || \
        claude -p "$user_message" --system-prompt "$critic_prompt" > "$critique_file"
    else
        local combined_prompt="${critic_prompt}

---

${user_message}"
        openclaw run --model "$model" --prompt "$combined_prompt" > "$critique_file"
    fi

    ok "参谋完成：$critique_file（$(wc -c < "$critique_file") bytes）"
}

# 调用裁判（评分）
run_judge() {
    local round=$1
    local draft_file="$WORK_DIR/round-${round}-draft.md"
    local critique_file="$WORK_DIR/round-${round}-critique.md"
    local judgment_file="$WORK_DIR/round-${round}-judgment.md"

    log "Round ${round}：裁判开始评分..."

    local judge_prompt
    judge_prompt=$(cat "$SKILL_DIR/judge-prompt.md")

    local task_brief
    task_brief=$(cat "$WORK_DIR/task-brief.md")

    local user_message="请对第${round}轮的草稿和参谋挑刺做出最终裁判。

===任务简报===
${task_brief}
=============

===当前草稿===
$(cat "$draft_file")
=============

===参谋挑刺===
$(cat "$critique_file")
=============

请严格按照裁判评分格式输出，给出总分、分项评分、裁决和理由。
${round} 轮中已经是第 ${round} 轮，最多 ${MAX_ROUNDS} 轮，请据此判断是否强制通过。"

    # 裁判用 Opus
    local model="claude-opus-4-5"
    if command -v claude &>/dev/null; then
        echo "$user_message" | claude --system "$judge_prompt" --model "$model" > "$judgment_file" 2>/dev/null || \
        claude -p "$user_message" --system-prompt "$judge_prompt" --model "$model" > "$judgment_file"
    else
        local combined_prompt="${judge_prompt}

---

${user_message}"
        openclaw run --model "$model" --prompt "$combined_prompt" > "$judgment_file"
    fi

    ok "裁判完成：$judgment_file（$(wc -c < "$judgment_file") bytes）"
}

# 生成 review-summary.md
generate_summary() {
    local total_rounds=$1
    local final_score=$2
    local summary_file="$WORK_DIR/review-summary.md"

    log "生成审核总结..."

    {
        echo "# 对抗式审核总结"
        echo ""
        echo "- **任务**：$(head -1 "$WORK_DIR/task-brief.md" | sed 's/主题：//')"
        echo "- **总轮次**：${total_rounds} 轮"
        echo "- **最终评分**：${final_score}/10"
        echo "- **审核时间**：$(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "---"
        echo ""

        for r in $(seq 1 "$total_rounds"); do
            echo "## Round ${r}"
            echo ""

            if [ -f "$WORK_DIR/round-${r}-draft.md" ]; then
                local draft_words
                draft_words=$(wc -w < "$WORK_DIR/round-${r}-draft.md" 2>/dev/null || echo "?")
                echo "**草稿字数**：${draft_words} 字"
                echo ""
            fi

            if [ -f "$WORK_DIR/round-${r}-critique.md" ]; then
                echo "**参谋主要批评**："
                grep -A2 "最重要的3件事" "$WORK_DIR/round-${r}-critique.md" 2>/dev/null | head -5 || echo "（见原文）"
                echo ""
            fi

            if [ -f "$WORK_DIR/round-${r}-judgment.md" ]; then
                local round_score
                round_score=$(extract_score "$WORK_DIR/round-${r}-judgment.md")
                echo "**裁判评分**：${round_score}/10"
                echo ""
                # 提取裁决结论
                grep -E "裁决[：:]" "$WORK_DIR/round-${r}-judgment.md" 2>/dev/null | head -1 || true
                echo ""
            fi

            echo "---"
            echo ""
        done

        echo "## 最终结果"
        echo ""
        if [ "$final_score" -ge "$PASS_SCORE" ]; then
            echo "✅ **通过**（${final_score}/10）"
        else
            echo "⚠️ **未完全达标**（${final_score}/10，未过${PASS_SCORE}分线，已输出当前最佳版本）"
        fi
        echo ""
        echo "最终稿件：\`final-draft.md\`"

    } > "$summary_file"

    ok "审核总结：$summary_file"
}

# ==================== 主流程 ====================

main() {
    log "对抗式内容审核启动"
    log "工作目录：$WORK_DIR"
    log "最大轮次：$MAX_ROUNDS，通过分数线：$PASS_SCORE"
    echo ""

    check_prereqs

    local current_round=1
    local final_score=0
    local passed=false

    while [ "$current_round" -le "$MAX_ROUNDS" ]; do
        echo ""
        log "========== Round ${current_round}/${MAX_ROUNDS} =========="

        # 1. 笔杆子写作
        run_writer "$current_round"

        # 2. 参谋挑刺
        run_critic "$current_round"

        # 3. 裁判评分
        run_judge "$current_round"

        # 4. 读取分数
        final_score=$(extract_score "$WORK_DIR/round-${current_round}-judgment.md")
        log "本轮评分：${final_score}/10"

        # 5. 判断是否通过
        if [ "$final_score" -ge "$PASS_SCORE" ]; then
            ok "通过！评分 ${final_score}/10 ≥ ${PASS_SCORE}"
            passed=true
            break
        else
            if [ "$current_round" -ge "$MAX_ROUNDS" ]; then
                warn "已达最大轮次（${MAX_ROUNDS}轮），输出当前最佳版本"
                break
            fi
            warn "未通过（${final_score}/10 < ${PASS_SCORE}），进入下一轮..."
            current_round=$((current_round + 1))
        fi
    done

    # 6. 输出最终稿
    local best_round=$current_round
    local final_draft="$WORK_DIR/final-draft.md"
    cp "$WORK_DIR/round-${best_round}-draft.md" "$final_draft"
    ok "最终稿已输出：$final_draft"

    # 7. 生成审核总结
    generate_summary "$current_round" "$final_score"

    echo ""
    if [ "$passed" = true ]; then
        ok "🎉 审核完成，${current_round}轮通过，评分：${final_score}/10"
    else
        warn "⚠️ 审核完成，${current_round}轮后未达标（${final_score}/10），已输出最佳版本"
    fi

    echo ""
    echo "产出文件："
    echo "  📄 final-draft.md       — 最终稿件"
    echo "  📊 review-summary.md    — 审核总结"
    for r in $(seq 1 "$current_round"); do
        echo "  Round ${r}: round-${r}-draft.md | round-${r}-critique.md | round-${r}-judgment.md"
    done
}

main "$@"
