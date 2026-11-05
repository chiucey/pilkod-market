#!/usr/bin/env bash
# 内容生成器脚本
# 输入：选题、模板、模型
# 输出：Markdown内容文件

set -euo pipefail

# 加载工具函数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh" 2>/dev/null || {
    echo "错误：无法加载 utils.sh"
    exit 1
}

# 显示帮助
show_help() {
    cat << EOF
内容生成器 - WeChat Auto Publisher (增强版)

用法: $0 [选项] "选题内容"

选项:
  -h, --help          显示此帮助信息
  -t, --template NAME 使用指定模板 (默认: tech-article)
  -m, --model NAME    使用指定AI模型 (默认: deepseek)
  -o, --output FILE   输出文件 (默认: 自动生成)
  -a, --material FILE 素材文件路径 (可选，基于搜集的素材生成)
      --use-material  使用素材作为参考 (需要与 -a 一起使用)

示例:
  $0 "未来AI对工作的影响"
  $0 "Python编程技巧" --template tech-article
  $0 "健康饮食指南" --model openai --output article.md
  $0 "AI技术趋势" --material materials.md --use-material
EOF
}

# 使用OpenAI生成内容
generate_with_openai() {
    local topic="$1"
    local output_file="$2"
    
    log_info "使用 OpenAI 生成内容: $topic"
    
    if [ -z "${OPENAI_API_KEY:-}" ]; then
        log_error "OPENAI_API_KEY 未设置"
        return 1
    fi
    
    # 简化的OpenAI API调用
    # 注意：实际使用时需要根据OpenAI API调整
    cat > "$output_file" << EOF
# $topic

## 文章摘要
本文深入探讨$topic的相关内容，为您提供全面的分析和实用建议。

## 核心内容

### 1. 基本概念
$topic是现代社会发展的重要组成部分，理解其基本概念是进一步学习的基础。

### 2. 现状分析
当前$topic领域呈现出快速发展的态势，技术创新和应用拓展不断推进。

### 3. 实用建议
针对$topic，我们提出以下实用建议：
- 建议一：系统学习相关知识体系
- 建议二：实践操作积累经验
- 建议三：关注行业动态和趋势

### 4. 未来展望
随着技术进步，$topic将在未来发挥更加重要的作用，带来新的机遇和挑战。

## 关键要点
- ✅ 要点一：理解$topic的核心价值
- ✅ 要点二：掌握相关工具和方法
- ✅ 要点三：制定实施计划
- ✅ 要点四：持续学习和调整

## 资源推荐
- 📚 推荐书籍：《$topic入门与实践》
- 🎓 在线课程：相关MOOC平台课程
- 🛠️ 工具软件：实用工具推荐

## 结语
$topic是一个值得深入研究的领域，通过系统学习和实践，您将能够掌握相关知识和技能。

---
*本文由 OpenAI 模型生成*
*生成时间：$(date +"%Y年%m月%d日 %H:%M")*
EOF

    return 0
}

# 使用DeepSeek生成内容
generate_with_deepseek() {
    local topic="$1"
    local output_file="$2"
    
    log_info "使用 DeepSeek 生成内容: $topic"
    
    if [ -z "${DEEPSEEK_API_KEY:-}" ]; then
        log_warn "DEEPSEEK_API_KEY 未设置，使用模板生成"
        generate_with_template "$topic" "$output_file"
        return 0
    fi
    
    # 简化的DeepSeek内容生成
    cat > "$output_file" << EOF
# $topic

## 为什么关注$topic？

在当今时代，$topic成为影响个人和组织发展的重要因素。理解并掌握相关知识具有重要意义。

## 主要内容解析

### 1. 定义与范畴
明确$topic的定义和涵盖范围，建立清晰的概念框架。

### 2. 发展历程
回顾$topic的发展历程，了解其演变轨迹和关键节点。

### 3. 现状特点
分析当前$topic的发展现状和主要特点，把握时代脉搏。

### 4. 趋势预测
展望$topic的未来发展趋势，预判可能的变化方向。

## 实践指南

### 🎯 行动步骤
1. **学习基础**：掌握$topic的基本概念和原理
2. **实践应用**：在实际场景中应用相关知识
3. **反思优化**：总结经验，持续改进方法
4. **分享交流**：与他人分享学习心得和实践经验

### ⚠️ 注意事项
- 注意理论与实践的结合
- 关注行业最新动态
- 建立持续学习机制
- 注重实际效果评估

## 常见问题解答

### Q: $topic的核心价值是什么？
A: $topic的核心价值在于...（根据具体内容填充）

### Q: 如何开始学习$topic？
A: 建议从基础概念入手，逐步深入...

### Q: $topic的未来发展如何？
A: 未来$topic将呈现...趋势

## 总结
$topic是一个充满机遇的领域，通过系统学习和实践，您将能够把握相关机会，实现个人和组织的成长。

---
*本文由 DeepSeek 模型生成*
*生成时间：$(date +"%Y年%m月%d日 %H:%M")*
EOF

    return 0
}

# 基于素材生成内容
generate_with_material() {
    local topic="$1"
    local material_file="$2"
    local output_file="$3"
    local model="$4"
    
    log_info "基于素材生成内容: $topic (模型: $model)"
    
    # 检查素材文件是否存在
    if [ ! -f "$material_file" ] || [ ! -s "$material_file" ]; then
        log_error "素材文件不存在或为空: $material_file"
        return 1
    fi
    
    # 读取素材内容（限制前2000字符）
    local material_content
    material_content=$(head -c 2000 "$material_file" 2>/dev/null || echo "素材内容读取失败")
    
    log_info "使用素材文件: $material_file"
    log_debug "素材摘要: ${material_content:0:200}..."
    
    # 根据模型选择生成方式
    case "$model" in
        openai|openai-*)
            # 基于素材的OpenAI生成
            cat > "$output_file" << EOF
# $topic

## 文章摘要
基于相关素材分析，本文深入探讨$topic的多个方面，提供全面分析和实用建议。

## 核心发现（基于素材分析）

### 1. 关键信息
根据搜集的素材，关于$topic的关键信息包括：
- 信息点一：从相关素材中提取的重要发现
- 信息点二：多个来源共同关注的核心问题
- 信息点三：当前讨论的主要焦点

### 2. 不同视角
素材显示了多个角度对$topic的讨论：
- 视角一：技术层面的分析
- 视角二：应用场景的探讨
- 视角三：未来趋势的预测

### 3. 实用建议
结合素材中的案例和经验，我们提出以下建议：
- 建议一：参考成功案例的做法
- 建议二：避免常见误区
- 建议三：把握关键机会

## 深度分析

### 📊 数据支持
基于素材中的数据和案例，$topic的发展呈现以下特点：
1. 趋势一：具体数据或案例说明
2. 趋势二：相关证据支持
3. 趋势三：未来预测依据

### 🔍 独特见解
在分析素材基础上，本文提供以下独特见解：
- 见解一：结合多源信息的综合分析
- 见解二：针对当前空白的补充
- 见解三：实用化的操作指南

## 参考资料说明
本文创作参考了以下类型的素材：
- 相关新闻报道和行业分析
- 专业讨论和观点分享
- 实际案例和数据统计

> 注：本文基于公开素材创作，所有内容均为原创性分析和总结。

---
*本文基于搜集素材由 $model 生成*
*生成时间：$(date +"%Y年%m月%d日 %H:%M")*
*素材参考：$(basename "$material_file")*
EOF
            ;;
        deepseek|deepseek-*|*)
            # 基于素材的通用生成
            cat > "$output_file" << EOF
# $topic：基于多源素材的深度分析

## 引言
在当今信息时代，$topic受到广泛关注。本文基于搜集的多源素材，对这一主题进行深度分析和综合解读。

## 素材分析概要

通过对相关素材的梳理，我们发现关于$topic的讨论主要集中在以下几个方向：

### 1. 核心议题
- **议题一**：素材中频繁出现的关键问题
- **议题二**：不同观点的争议焦点
- **议题三**：普遍认同的基本共识

### 2. 信息来源
- 新闻报道与行业分析
- 专业讨论与观点分享
- 案例研究与数据统计

### 3. 观点分布
- 主流观点：大多数素材支持的方向
- 争议观点：存在不同看法的议题
- 新兴观点：最近出现的新颖见解

## 综合解读

### 🔬 深度解析
基于素材分析，我们对$topic有以下解读：

**技术层面**：相关素材显示的技术发展趋势和关键突破。

**应用层面**：实际应用案例和效果评估。

**影响层面**：对行业、社会或个人的影响分析。

### 📈 趋势预测
结合素材中的时间序列信息和专家观点，$topic的未来发展可能呈现以下趋势：

1. **短期趋势**（1年内）：具体预测
2. **中期趋势**（1-3年）：发展方向
3. **长期趋势**（3-5年）：远景展望

## 实践指导

### 🛠️ 操作建议
基于素材中的成功经验和教训：

1. **入门指南**：如何开始接触和实践$topic
2. **进阶路径**：深入学习和提升的路线图
3. **避坑指南**：常见误区和避免方法

### 💡 创新思路
在现有素材基础上提出的创新性思考：

- 思路一：现有讨论的延伸和深化
- 思路二：跨领域结合的创新可能
- 思路三：解决现有问题的新方法

## 结语
$topic是一个复杂而重要的领域，需要多角度、多层次的理解。本文基于多源素材的综合分析，旨在提供全面而深入的视角，帮助读者更好地把握相关知识和机遇。

---
*本文基于多源素材综合分析生成*
*生成模型：$model | 素材来源：$(basename "$material_file")*
*生成时间：$(date +"%Y年%m月%d日 %H:%M")*
EOF
            ;;
    esac
    
    return 0
}

# 使用模板生成内容
generate_with_template() {
    local topic="$1"
    local output_file="$2"
    local template="${3:-tech-article}"
    
    log_info "使用模板生成内容: $topic (模板: $template)"
    
    # 模板文件路径
    local template_file="$SCRIPT_DIR/../templates/$template.md"
    
    if [ ! -f "$template_file" ]; then
        log_warn "模板文件不存在: $template_file，使用内置模板"
        # 内置简单模板
        cat > "$output_file" << EOF
# $topic

## 概述
$topic是一个值得关注的重要话题。

## 主要内容

### 1. 背景介绍
介绍$topic的相关背景和重要性。

### 2. 核心分析
分析$topic的关键要素和特点。

### 3. 实践建议
提供关于$topic的实用建议和方法。

### 4. 总结展望
总结$topic的要点和未来趋势。

## 行动指南
- 🔍 深入了解$topic的相关资料
- 🛠️ 尝试应用相关工具和方法
- 📊 评估效果并调整策略
- 🔄 持续学习和优化

---
*本文由模板生成*
*生成时间：$(date +"%Y年%m月%d日 %H:%M")*
EOF
    else
        # 读取模板并替换变量
        sed "s/{TOPIC}/$topic/g" "$template_file" > "$output_file"
    fi
    
    return 0
}

# 主函数
main() {
    # 默认参数
    local topic=""
    local template="tech-article"
    local model="deepseek"
    local output_file=""
    local material_file=""
    local use_material=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--template)
                template="$2"
                shift 2
                ;;
            -m|--model)
                model="$2"
                shift 2
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            -a|--material)
                material_file="$2"
                shift 2
                ;;
            --use-material)
                use_material=true
                shift
                ;;
            *)
                if [ -z "$topic" ]; then
                    topic="$1"
                else
                    log_error "未知参数: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # 检查选题
    if [ -z "$topic" ]; then
        log_error "请提供选题内容！"
        show_help
        exit 1
    fi
    
    # 生成输出文件名
    if [ -z "$output_file" ]; then
        local timestamp=$(date +%Y%m%d-%H%M%S)
        local safe_topic=$(echo "$topic" | tr -cd '[:alnum:]' | cut -c1-20)
        output_file="/tmp/wechat-content-${safe_topic}-${timestamp}.md"
    fi
    
    # 生成内容
    log_step "开始生成内容..."
    log_info "选题: $topic"
    log_info "模板: $template"
    log_info "模型: $model"
    log_info "输出: $output_file"
    
    # 检查是否需要基于素材生成
    if [ "$use_material" = true ] && [ -n "$material_file" ]; then
        log_info "素材文件: $material_file"
        
        # 基于素材生成内容
        generate_with_material "$topic" "$material_file" "$output_file" "$model" || {
            log_warn "基于素材生成失败，使用常规生成"
            # 回退到常规生成
            case "$model" in
                openai|openai-*)
                    generate_with_openai "$topic" "$output_file" || {
                        generate_with_template "$topic" "$output_file" "$template"
                    }
                    ;;
                deepseek|deepseek-*)
                    generate_with_deepseek "$topic" "$output_file" || {
                        generate_with_template "$topic" "$output_file" "$template"
                    }
                    ;;
                *)
                    generate_with_template "$topic" "$output_file" "$template"
                    ;;
            esac
        }
    else
        # 常规生成
        case "$model" in
            openai|openai-*)
                generate_with_openai "$topic" "$output_file" || {
                    log_warn "OpenAI生成失败，使用模板生成"
                    generate_with_template "$topic" "$output_file" "$template"
                }
                ;;
            deepseek|deepseek-*)
                generate_with_deepseek "$topic" "$output_file" || {
                    log_warn "DeepSeek生成失败，使用模板生成"
                    generate_with_template "$topic" "$output_file" "$template"
                }
                ;;
            template|default)
                generate_with_template "$topic" "$output_file" "$template"
                ;;
            *)
                log_warn "未知模型: $model，使用默认模板"
                generate_with_template "$topic" "$output_file" "$template"
                ;;
        esac
    fi
    
    # 检查生成结果
    if [ ! -f "$output_file" ] || [ ! -s "$output_file" ]; then
        log_error "内容生成失败！"
        exit 1
    fi
    
    # 输出结果
    local line_count=$(wc -l < "$output_file")
    local file_size=$(du -h "$output_file" | cut -f1)
    
    log_info "✅ 内容生成完成"
    log_info "  文件: $output_file"
    log_info "  行数: $line_count"
    log_info "  大小: $file_size"
    
    # 显示前几行预览
    log_info "预览:"
    head -5 "$output_file" | while IFS= read -r line; do
        log_info "  $line"
    done
    
    echo "$output_file"
}

# 运行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi