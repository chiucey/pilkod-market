# ============================================================================
# SCI期刊标准配色方案
# Scientific Color Palettes for Publication
# ============================================================================
# 作者：Bioinformatics Analysis Pipeline
# 版本：1.0.0
# ============================================================================

# ============================================================================
# 1. 经典SCI配色方案
# ============================================================================

#' Nature期刊标准配色
#' 适用于大多数生命科学图表
NATURE_PALETTE <- c(
  "#E64B35",  # 红色 - 上调/处理组
  "#4DBBD5",  # 青色 - 下调/对照组
  "#00A087",  # 绿色 - 富集/激活
  "#3C5488",  # 深蓝 - 主要分组
  "#F39B7F",  # 橙色 - 强调
  "#8491B4",  # 灰蓝 - 次要
  "#91D1C2",  # 浅绿 - 辅助
  "#DC0000",  # 深红 - 重要标记
  "#7E6148",  # 棕色 - 注释
  "#B09C85"   # 浅棕 - 背景
)

#' Science期刊配色
#' 蓝绿渐变系，适合连续变量
SCIENCE_PALETTE <- c(
  "#3B4992",  # 深蓝
  "#5A74C0",  # 中蓝
  "#7F9EE0",  # 浅蓝
  "#A0AAFF",  # 极浅蓝
  "#C4C4FF",  # 极浅
  "#E0E0E0",  # 中灰
  "#FFA4A4",  # 极浅红
  "#FF7373",  # 浅红
  "#E03C3C",  # 中红
  "#B30000"   # 深红
)

#' Cell期刊配色
#' 高对比度，适合复杂图表
CELL_PALETTE <- c(
  "#4A2882",  # 紫色
  "#F37B20",  # 橙色
  "#1F77B4",  # 蓝色
  "#2DA10C",  # 绿色
  "#BB2020",  # 红色
  "#7B43A0",  # 浅紫
  "#F2B90C",  # 金色
  "#089099",  # 青色
  "#8C563B",  # 棕色
  "#666666"   # 灰色
)

# ============================================================================
# 2. 色盲友好配色方案
# ============================================================================

#' 色盲友好配色 - Paul Tol
#' 适合红绿色盲读者
COLORBLIND_PALETTE <- c(
  "#0173B2",  # 深蓝
  "#DE8F05",  # 橙黄
  "#029E73",  # 青绿
  "#CC78BC",  # 粉紫
  "#CA9161",  # 棕橙
  "#949494",  # 灰色
  "#ECE133",  # 亮黄
  "#56B4E9"   # 天蓝
)

#' 色盲安全三色方案
#' 仅使用蓝-黄-红，适合二元对比
DIVERGING_BWR <- c(
  "#0072B2",  # 蓝色 (低/负)
  "#E0E0E0",  # 灰色 (中性)
  "#D55E00"   # 橙色 (高/正)
)

# ============================================================================
# 3. 连续变量配色
# ============================================================================

#' Viridis配色（推荐）
#' 感知均匀、高对比度、打印友好
VIRIDIS_PALETTE <- c(
  "#440154",  # 深紫
  "#482878",  # 紫蓝
  "#3E4A89",  # 蓝紫
  "#31688E",  # 蓝
  "#26828E",  # 青蓝
  "#1F9E89",  # 青绿
  "#35B779",  # 绿
  "#6DCD59",  # 浅绿
  "#B4DE2C",  # 黄绿
  "#FDE725"   # 黄
)

#' Plasma配色
#' 适合热图和密度图
PLASMA_PALETTE <- c(
  "#0D0887",  # 深蓝紫
  "#5B02A3",  # 紫色
  "#9A179B",  # 品红
  "#CC4778",  # 粉红
  "#ED6925",  # 橙色
  "#F89540",  # 浅橙
  "#F0F921"   # 黄色
)

#' Magma配色
#' 适合暗背景图表
MAGMA_PALETTE <- c(
  "#000004",  # 黑色
  "#180F3E",  # 深紫
  "#440F76",  # 紫色
  "#721F81",  # 品红
  "#9F2F7F",  # 粉红
  "#CD4071",  # 玫瑰
  "#F1605D",  # 珊瑚
  "#FD9567",  # 橙粉
  "#FEC98D"   # 米黄
)

#' Inferno配色
#' 高动态范围，适合科技图表
INFERNO_PALETTE <- c(
  "#000004",  # 黑色
  "#1B0C41",  # 深紫
  "#4A0C6B",  # 紫色
  "#781C6D",  # 深粉
  "#A52C60",  # 红粉
  "#CF4446",  # 红色
  "#ED6925",  # 橙色
  "#FB9B06",  # 金橙
  "#F7D13D"   # 黄色
)

# ============================================================================
# 4. 功能性配色函数
# ============================================================================

#' 获取差异基因配色
#' @param alpha 透明度
#' @return 命名向量
get_deg_colors <- function(alpha = 0.7) {
  c(
    "Up" = adjustcolor("#E64B35", alpha.f = alpha),
    "Down" = adjustcolor("#4DBBD5", alpha.f = alpha),
    "Not Significant" = adjustcolor("#CCCCCC", alpha.f = alpha)
  )
}

#' 获取分组配色
#' @param n 组数
#' @param palette 配色方案
#' @return 颜色向量
get_group_colors <- function(n, palette = NATURE_PALETTE) {
  if (n <= length(palette)) {
    return(palette[1:n])
  } else {
    return(colorRampPalette(palette)(n))
  }
}

#' 获取渐变配色
#' @param n 渐变级数
#' @param palette 配色方案
#' @param reverse 是否反转
#' @return 颜色向量
get_gradient_colors <- function(n, palette = VIRIDIS_PALETTE, reverse = FALSE) {
  colors <- colorRampPalette(palette)(n)
  if (reverse) {
    return(rev(colors))
  }
  return(colors)
}

#' 预览配色方案
#' @param palette_name 配色名称
#' @param n 显示颜色数
preview_palette <- function(palette_name = "NATURE", n = 10) {
  palette <- switch(
    palette_name,
    "NATURE" = NATURE_PALETTE,
    "SCIENCE" = SCIENCE_PALETTE,
    "CELL" = CELL_PALETTE,
    "COLORBLIND" = COLORBLIND_PALETTE,
    "VIRIDIS" = VIRIDIS_PALETTE,
    "PLASMA" = PLASMA_PALETTE,
    "MAGMA" = MAGMA_PALETTE,
    "INFERNO" = INFERNO_PALETTE
  )

  n_display <- min(n, length(palette))
  colors <- colorRampPalette(palette)(n_display)

  # 创建预览图
  df <- data.frame(
    x = 1:n_display,
    y = 1,
    color = colors
  )

  p <- ggplot(df, aes(x = x, y = y, fill = color)) +
    geom_tile(width = 1, height = 1) +
    scale_fill_identity() +
    theme_void() +
    labs(title = paste("Palette:", palette_name)) +
    theme(plot.title = element_text(hjust = 0.5, size = 14, face = "bold"))

  print(p)
  return(invisible(colors))
}

# ============================================================================
# 5. 主题预设
# ============================================================================

#' SCI标准主题
#' @param base_size 基础字体大小
#' @param base_family 基础字体
#' @return theme对象
theme_sci_publication <- function(base_size = 10, base_family = "Arial") {
  theme_classic(base_size = base_size, base_family = base_family) +
    theme(
      # 面板设置
      panel.border = element_rect(fill = NA, color = "black", linewidth = 0.5),
      panel.background = element_rect(fill = "white"),

      # 轴设置
      axis.line = element_blank(),
      axis.ticks = element_line(color = "black", linewidth = 0.5),
      axis.ticks.length = unit(2, "pt"),

      # 文字设置
      text = element_text(color = "black"),
      plot.title = element_text(size = 12, face = "bold", hjust = 0),

      # 图例设置
      legend.background = element_blank(),
      legend.box.background = element_rect(fill = NA, color = NA),
      legend.key.size = unit(8, "pt"),
      legend.text = element_text(size = 9),

      # 网格线
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank()
    )
}

#' Nature风格主题
#' @return theme对象
theme_nature <- function() {
  theme_sci_publication() +
    theme(
      legend.position = "right",
      plot.margin = margin(t = 10, r = 10, b = 10, l = 10),
      strip.background = element_blank()
    )
}

#' 无网格主题
#' @return theme对象
theme_minimal_grid <- function() {
  theme_sci_publication() +
    theme(
      panel.grid.major = element_line(color = "grey90", linewidth = 0.3),
      panel.grid.minor = element_blank()
    )
}

# ============================================================================
# 6. 图表模板
# ============================================================================

#' 创建分面条形图
#' @param data 数据框
#' @param x_var x轴变量
#' @param fill_var 填充变量
#' @param palette 配色方案
#' @return ggplot2对象
faceted_barplot_template <- function(data, x_var, fill_var, palette = NATURE_PALETTE) {
  ggplot(data, aes_string(x = x_var, fill = fill_var)) +
    geom_bar(position = "dodge", color = "black", linewidth = 0.3) +
    scale_fill_manual(values = palette) +
    theme_sci_publication() +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1),
      legend.position = "top"
    ) +
    labs(x = "", y = "Count", fill = "")
}

#' 创建带误差线的点图
#' @param data 数据框
#' @param x_var x轴变量
#' @param y_var y轴变量
#' @param group_var 分组变量
#' @param ymin_var y最小值
#' @param ymax_var y最大值
#' @param palette 配色方案
#' @return ggplot2对象
point_errorbar_template <- function(data, x_var, y_var, group_var,
                                    ymin_var, ymax_var,
                                    palette = NATURE_PALETTE) {
  ggplot(data, aes_string(x = x_var, y = y_var,
                         color = group_var, group = group_var)) +
    geom_point(position = position_dodge(0.3), size = 2) +
    geom_errorbar(
      aes_string(ymin = ymin_var, ymax = ymax_var),
      position = position_dodge(0.3),
      width = 0.2
    ) +
    scale_color_manual(values = palette) +
    theme_sci_publication() +
    labs(x = "", y = "Expression", color = "")
}

# ============================================================================
# 7. 导出函数
# ============================================================================

#' 导出配色方案为CSS
#' @param filename 输出文件名
#' @param palette_name 配色名称
export_palette_css <- function(filename, palette_name = "NATURE") {
  palette <- get_group_colors(10, get(paste0(toupper(palette_name), "_PALETTE")))

  css <- paste0(
    ":root {\n",
    "  /* ", palette_name, " Color Palette */\n",
    paste0(
      "  --color-", seq_along(palette), ": ", palette, ";\n"
    ),
    "}\n"
  )

  writeLines(css, filename)
  message("CSS exported to: ", filename)
}

#' 导出配色方案为Python dict
#' @param filename 输出文件名
#' @param palette_name 配色名称
export_palette_python <- function(filename, palette_name = "NATURE") {
  palette <- get_group_colors(10, get(paste0(toupper(palette_name), "_PALETTE")))

  py_code <- paste0(
    "# ", palette_name, " Color Palette\n",
    "COLOR_PALETTE = {\n",
    paste0(
      '    "color_', seq_along(palette), '": "', palette, '",\n'
    ),
    "}\n"
  )

  writeLines(py_code, filename)
  message("Python dict exported to: ", filename)
}

# ============================================================================
# 8. 演示代码
# ============================================================================

# 演示配色预览
if (interactive()) {
  # 查看所有配色方案
  preview_palette("NATURE")
  preview_palette("VIRIDIS")
  preview_palette("COLORBLIND")

  # 创建示例图
  set.seed(42)
  demo_data <- data.frame(
    group = rep(c("Control", "Treatment"), each = 50),
    value = c(rnorm(50, 0, 1), rnorm(50, 1.5, 1)),
    category = rep(letters[1:5], each = 20)
  )

  # 示例1：差异基因火山图配色
  ggplot(demo_data, aes(x = value, y = abs(value), color = group)) +
    geom_point(alpha = 0.7, size = 3) +
    scale_color_manual(values = get_deg_colors()) +
    theme_nature()

  # 示例2：分组条形图配色
  ggplot(demo_data, aes(x = category, fill = group)) +
    geom_bar(position = "dodge", color = "black", linewidth = 0.3) +
    scale_fill_manual(values = NATURE_PALETTE[1:2]) +
    theme_sci_publication()

  # 示例3：热图配色
  heatmap_matrix <- matrix(rnorm(100), nrow = 10)
  rownames(heatmap_matrix) <- paste0("Gene", 1:10)
  colnames(heatmap_matrix) <- paste0("Sample", 1:10)

  pheatmap(heatmap_matrix,
           color = colorRampPalette(VIRIDIS_PALETTE)(100),
           scale = "row",
           show_rownames = TRUE,
           show_colnames = TRUE)
}
