-- 提示词巧匠升级版 - 数据库初始化脚本
-- 版本：v2.0.0 - 数据库增强版
-- 创建日期：2025-03-19
-- 基于项目：机关接待信息自动化处理系统的成功实践

-- 创建数据库
CREATE DATABASE IF NOT EXISTS prompt_builder_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE prompt_builder_db;

-- =====================================================
-- 表1：prompts（提示词主表）
-- =====================================================
CREATE TABLE prompts (
  prompt_id VARCHAR(50) PRIMARY KEY COMMENT '提示词唯一标识',
  user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
  scenario VARCHAR(100) NOT NULL COMMENT '使用场景',
  goal_orientation VARCHAR(50) NOT NULL COMMENT '目标导向',
  is_efficiency_priority BOOLEAN DEFAULT FALSE COMMENT '是否效率优先',
  is_accuracy_priority BOOLEAN DEFAULT FALSE COMMENT '是否准确性优先',
  prompt_content TEXT NOT NULL COMMENT '提示词全文',
  score INT DEFAULT 0 COMMENT '评分(0-100)',
  mode VARCHAR(20) NOT NULL COMMENT '生成模式(fast/precision)',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  is_favorite BOOLEAN DEFAULT FALSE COMMENT '是否收藏',
  use_count INT DEFAULT 0 COMMENT '使用次数',
  tags TEXT COMMENT '标签(逗号分隔)',
  INDEX idx_user_id (user_id),
  INDEX idx_scenario (scenario),
  INDEX idx_score (score),
  INDEX idx_created_at (created_at),
  INDEX idx_is_favorite (is_favorite)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='提示词主表';

-- =====================================================
-- 表2：prompt_dimensions（提示词维度详情表）
-- =====================================================
CREATE TABLE prompt_dimensions (
  dimension_id INT AUTO_INCREMENT PRIMARY KEY,
  prompt_id VARCHAR(50) NOT NULL COMMENT '提示词ID',
  identity VARCHAR(200) COMMENT '角色设定',
  target_audience VARCHAR(200) COMMENT '目标受众',
  style VARCHAR(200) COMMENT '语言风格',
  structure VARCHAR(200) COMMENT '内容结构',
  output_format VARCHAR(200) COMMENT '输出格式',
  thinking_depth VARCHAR(200) COMMENT '思维深度',
  creativity VARCHAR(200) COMMENT '创意水平',
  professionalism VARCHAR(200) COMMENT '专业性',
  practicality VARCHAR(200) COMMENT '实用性',
  operability VARCHAR(200) COMMENT '可操作性',
  clarity VARCHAR(200) COMMENT '清晰度',
  completeness VARCHAR(200) COMMENT '完整性',
  flexibility VARCHAR(200) COMMENT '灵活性',
  adaptability VARCHAR(200) COMMENT '适配性',
  FOREIGN KEY (prompt_id) REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  INDEX idx_prompt_id (prompt_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='提示词维度详情表';

-- =====================================================
-- 表3：prompt_versions（提示词版本历史表）
-- =====================================================
CREATE TABLE prompt_versions (
  version_id INT AUTO_INCREMENT PRIMARY KEY,
  prompt_id VARCHAR(50) NOT NULL COMMENT '提示词ID',
  version_number INT NOT NULL COMMENT '版本号',
  prompt_content TEXT NOT NULL COMMENT '提示词内容',
  score INT DEFAULT 0 COMMENT '评分',
  change_reason VARCHAR(500) COMMENT '修改原因',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (prompt_id) REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  INDEX idx_prompt_id (prompt_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='提示词版本历史表';

-- =====================================================
-- 表4：prompt_templates（提示词模板表）
-- =====================================================
CREATE TABLE prompt_templates (
  template_id VARCHAR(50) PRIMARY KEY COMMENT '模板ID',
  template_name VARCHAR(200) NOT NULL COMMENT '模板名称',
  scenario VARCHAR(100) NOT NULL COMMENT '适用场景',
  template_content TEXT NOT NULL COMMENT '模板内容',
  is_public BOOLEAN DEFAULT TRUE COMMENT '是否公开',
  usage_count INT DEFAULT 0 COMMENT '使用次数',
  avg_score DECIMAL(3,1) DEFAULT 0.0 COMMENT '平均评分',
  created_by VARCHAR(50) COMMENT '创建者',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_scenario (scenario),
  INDEX idx_is_public (is_public)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='提示词模板表';

-- =====================================================
-- 插入示例模板数据
-- =====================================================
INSERT INTO prompt_templates (template_id, template_name, scenario, template_content, is_public, created_by) VALUES
('TPL001', '产品文案写作模板', '文案撰写', '你是一位拥有{years}年经验的{role}。请为{product}撰写一篇面向{target_audience}的产品介绍文案，突出{key_features}。文案风格应{style}，适合{platform}。字数控制在{word_count}字，采用{structure}结构。产品核心参数：{product_params}。', TRUE, 'system'),
('TPL002', '技术文档生成模板', '文档处理', '你是一位{role}，请为{project}撰写{document_type}。目标读者是{target_audience}。文档应包含以下部分：{sections}。使用{language}语言，采用{style}风格。确保内容的准确性和专业性。', TRUE, 'system'),
('TPL003', '会议纪要模板', '会议纪要', '请根据以下会议内容整理会议纪要：\n\n会议主题：{meeting_topic}\n参会人员：{attendees}\n会议时间：{meeting_time}\n\n会议内容：{meeting_content}\n\n请按以下格式整理：\n1. 会议概要\n2. 主要议题\n3. 决策事项\n4. 行动计划\n5. 待办事项（含负责人和截止日期）', TRUE, 'system'),
('TPL004', '代码生成模板', '代码编程', '你是一位拥有{years}年经验的{language}开发工程师。请编写一个{task_type}，具体需求如下：\n\n需求描述：{requirements}\n\n功能要求：\n{functional_requirements}\n\n技术要求：\n{technical_requirements}\n\n代码风格：{code_style}\n注释要求：{comment_style}', TRUE, 'system'),
('TPL005', '数据分析报告模板', '文档处理', '你是一位数据分析师。请根据以下数据分析需求生成报告：\n\n分析目标：{analysis_goal}\n数据来源：{data_source}\n分析维度：{dimensions}\n关键指标：{metrics}\n\n报告应包含：\n1. 数据概览\n2. 关键发现\n3. 趋势分析\n4. 结论与建议\n\n报告风格：{report_style}\n图表类型：{chart_types}', TRUE, 'system');

-- =====================================================
-- 创建视图：提示词统计视图
-- =====================================================
CREATE VIEW prompt_statistics AS
SELECT 
    user_id,
    COUNT(*) as total_prompts,
    COUNT(CASE WHEN score >= 90 THEN 1 END) as high_quality_count,
    COUNT(CASE WHEN is_favorite = TRUE THEN 1 END) as favorite_count,
    SUM(use_count) as total_uses,
    AVG(score) as avg_score,
    MAX(created_at) as last_created_at
FROM prompts
GROUP BY user_id;

-- =====================================================
-- 创建存储过程：更新提示词使用统计
-- =====================================================
DELIMITER //
CREATE PROCEDURE update_prompt_usage(IN p_prompt_id VARCHAR(50), IN p_action VARCHAR(20))
BEGIN
    IF p_action = 'use' THEN
        UPDATE prompts SET use_count = use_count + 1 WHERE prompt_id = p_prompt_id;
    ELSEIF p_action = 'favorite' THEN
        UPDATE prompts SET is_favorite = NOT is_favorite WHERE prompt_id = p_prompt_id;
    END IF;
END //
DELIMITER ;

-- =====================================================
-- 创建存储过程：获取推荐提示词
-- =====================================================
DELIMITER //
CREATE PROCEDURE get_recommended_prompts(IN p_user_id VARCHAR(50), IN p_scenario VARCHAR(100), IN p_limit INT)
BEGIN
    DECLARE sql_query TEXT;
    
    SET sql_query = CONCAT(
        'SELECT p.*, d.* FROM prompts p ',
        'LEFT JOIN prompt_dimensions d ON p.prompt_id = d.prompt_id ',
        'WHERE p.score >= 90 AND p.user_id = ? ',
        CASE WHEN p_scenario IS NOT NULL THEN CONCAT('AND p.scenario = ? ') ELSE '' END,
        'ORDER BY p.use_count DESC, p.score DESC ',
        'LIMIT ?'
    );
    
    IF p_scenario IS NOT NULL THEN
        SET @sql = sql_query;
        PREPARE stmt FROM @sql;
        EXECUTE stmt USING p_user_id, p_scenario, p_limit;
    ELSE
        SET @sql = sql_query;
        PREPARE stmt FROM @sql;
        EXECUTE stmt USING p_user_id, p_limit;
    END IF;
    
    DEALLOCATE PREPARE stmt;
END //
DELIMITER ;

-- =====================================================
-- 数据库版本信息表
-- =====================================================
CREATE TABLE db_version (
    version_id INT PRIMARY KEY AUTO_INCREMENT,
    version_number VARCHAR(20) NOT NULL UNIQUE,
    version_name VARCHAR(100),
    release_date DATE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据库版本信息表';

-- 插入版本信息
INSERT INTO db_version (version_number, version_name, release_date, description) VALUES
('2.0.0', '数据库增强版', '2025-03-19', '基于机关接待信息自动化处理系统的成功实践，增加数据库持久化、智能检索、资产管理功能');

-- =====================================================
-- 完成提示
-- =====================================================
SELECT '✅ 数据库初始化完成！' AS status;
SELECT CONCAT('📊 已创建 ', COUNT(*), ' 张表') AS table_count FROM information_schema.tables WHERE table_schema = 'prompt_builder_db';
SELECT CONCAT('📝 已插入 ', COUNT(*), ' 个示例模板') AS template_count FROM prompt_templates;
SELECT '🚀 现在可以开始使用提示词巧匠升级版了！' AS next_step;
