"""
TikTok Mini Game Generator
TikTok小游戏生成器 - 零代码游戏生成指南

支持多种零代码游戏制作工具的游戏生成模板
"""

# ============================================================
# 零代码游戏生成工具推荐
# ============================================================

NOCODE_TOOLS = {
    "construct_3": {
        "name": "Construct 3",
        "description": "网页可视化游戏开发工具，无需编程基础",
        "website": "https://www.construct.net/",
        "pricing": "免费版有限制，付费版$99/年起",
        "export_targets": ["HTML5", "iOS", "Android", "TikTok Mini Game"],
        "pros": ["无需编码", "社区活跃", "导出选项多"],
        "cons": ["高级功能需付费", "性能一般"]
    },
    "buildbox": {
        "name": "Buildbox",
        "description": "3D游戏可视化开发工具",
        "website": "https://www.buildbox.com/",
        "pricing": "$99/月起",
        "export_targets": ["HTML5", "iOS", "Android"],
        "pros": ["支持3D", "模板丰富"],
        "cons": ["导出TikTok需要额外步骤"]
    },
    "gdevelop": {
        "name": "GDevelop",
        "description": "开源免费游戏引擎",
        "website": "https://gdevelop.io/",
        "pricing": "免费开源",
        "export_targets": ["HTML5", "iOS", "Android"],
        "pros": ["完全免费", "开源社区", "功能丰富"],
        "cons": ["TikTok导出需转换"]
    },
    "playcanvas": {
        "name": "PlayCanvas",
        "description": "基于Web的3D游戏引擎",
        "website": "https://playcanvas.com/",
        "pricing": "免费版有限制",
        "export_targets": ["HTML5", "TikTok Mini Game"],
        "pros": ["3D能力强", "团队协作", "TikTok原生支持"],
        "cons": ["学习曲线较陡"]
    }
}


# ============================================================
# 快速游戏模板代码
# ============================================================

FLAPPY_BIRD_TEMPLATE = '''
<!-- 简化版Flappy Bird游戏 - 可直接运行 -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flappy Bird Clone</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { display: flex; justify-content: center; align-items: center; height: 100vh; background: #70c5ce; }
        canvas { border: 4px solid #543847; border-radius: 8px; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="400" height="600"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        // 游戏状态
        let gameRunning = false;
        let score = 0;
        let highScore = localStorage.getItem('flappyHighScore') || 0;

        // 小鸟
        const bird = {
            x: 100,
            y: 300,
            width: 40,
            height: 30,
            velocity: 0,
            gravity: 0.5,
            jump: -8
        };

        // 管道
        let pipes = [];
        const pipeWidth = 60;
        const pipeGap = 150;
        let pipeSpeed = 3;

        // 绘制背景
        function drawBackground() {
            ctx.fillStyle = '#70c5ce';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        }

        // 绘制小鸟
        function drawBird() {
            ctx.fillStyle = '#ffcc00';
            ctx.beginPath();
            ctx.ellipse(bird.x, bird.y, bird.width/2, bird.height/2, 0, 0, Math.PI * 2);
            ctx.fill();

            // 眼睛
            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(bird.x + 10, bird.y - 5, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#000';
            ctx.beginPath();
            ctx.arc(bird.x + 12, bird.y - 5, 4, 0, Math.PI * 2);
            ctx.fill();

            // 嘴巴
            ctx.fillStyle = '#ff6600';
            ctx.beginPath();
            ctx.moveTo(bird.x + 20, bird.y);
            ctx.lineTo(bird.x + 30, bird.y + 5);
            ctx.lineTo(bird.x + 20, bird.y + 10);
            ctx.fill();
        }

        // 创建管道
        function createPipe() {
            const minHeight = 100;
            const maxHeight = canvas.height - pipeGap - minHeight;
            const topHeight = Math.random() * (maxHeight - minHeight) + minHeight;

            pipes.push({
                x: canvas.width,
                topHeight: topHeight,
                passed: false
            });
        }

        // 绘制管道
        function drawPipes() {
            ctx.fillStyle = '#76c953';
            pipes.forEach(pipe => {
                // 上管道
                ctx.fillRect(pipe.x, 0, pipeWidth, pipe.topHeight);
                // 下管道
                ctx.fillRect(pipe.x, pipe.topHeight + pipeGap, pipeWidth, canvas.height);
                // 装饰
                ctx.fillStyle = '#5da83f';
                ctx.fillRect(pipe.x + 5, 0, pipeWidth - 10, pipe.topHeight);
                ctx.fillRect(pipe.x + 5, pipe.topHeight + pipeGap, pipeWidth - 10, canvas.height);
                ctx.fillStyle = '#543847';
                ctx.fillRect(pipe.x, pipe.topHeight - 20, pipeWidth, 20);
                ctx.fillRect(pipe.x, pipe.topHeight + pipeGap, pipeWidth, 20);
                ctx.fillStyle = '#76c953';
            });
        }

        // 更新游戏
        function update() {
            if (!gameRunning) return;

            // 小鸟物理
            bird.velocity += bird.gravity;
            bird.y += bird.velocity;

            // 管道移动
            pipes.forEach(pipe => {
                pipe.x -= pipeSpeed;
            });

            // 移除出界管道
            pipes = pipes.filter(pipe => pipe.x > -pipeWidth);

            // 碰撞检测
            if (bird.y + bird.height/2 > canvas.height || bird.y - bird.height/2 < 0) {
                gameOver();
            }

            pipes.forEach(pipe => {
                if (bird.x + bird.width/2 > pipe.x && bird.x - bird.width/2 < pipe.x + pipeWidth) {
                    if (bird.y - bird.height/2 < pipe.topHeight || bird.y + bird.height/2 > pipe.topHeight + pipeGap) {
                        gameOver();
                    }
                }
                // 计分
                if (!pipe.passed && pipe.x + pipeWidth < bird.x) {
                    pipe.passed = true;
                    score++;
                }
            });
        }

        // 绘制分数
        function drawScore() {
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 40px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(score, canvas.width/2, 60);
            ctx.font = '16px Arial';
            ctx.fillText('最高分: ' + highScore, canvas.width/2, 90);
        }

        // 游戏结束
        function gameOver() {
            gameRunning = false;
            if (score > highScore) {
                highScore = score;
                localStorage.setItem('flappyHighScore', highScore);
            }
            // 显示激励视频广告按钮
            showRewardedAdButton();
        }

        // 显示激励视频按钮
        function showRewardedAdButton() {
            ctx.fillStyle = '#ff6600';
            ctx.fillRect(canvas.width/2 - 80, canvas.height/2, 160, 50);
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 18px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('看广告复活', canvas.width/2, canvas.height/2 + 30);
        }

        // 重新开始
        function restart() {
            bird.y = 300;
            bird.velocity = 0;
            pipes = [];
            score = 0;
            gameRunning = true;
        }

        // 渲染循环
        function gameLoop() {
            drawBackground();
            drawPipes();
            drawBird();
            drawScore();
            update();
            requestAnimationFrame(gameLoop);
        }

        // 点击控制
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            if (!gameRunning && score === 0) {
                restart();
                bird.velocity = bird.jump;
            } else if (!gameRunning && y > canvas.height/2 && y < canvas.height/2 + 50) {
                // 点击复活按钮 - 模拟激励视频
                console.log('显示激励视频广告...');
                setTimeout(() => {
                    restart();
                    bird.velocity = bird.jump;
                }, 1500);
            } else if (gameRunning) {
                bird.velocity = bird.jump;
            }
        });

        // 自动生成管道
        setInterval(() => {
            if (gameRunning) createPipe();
        }, 2000);

        // 开始
        gameLoop();
    </script>
</body>
</html>
'''

# ============================================================
# TikTok Mini Game 导出配置
# ============================================================

TIKTOK_EXPORT_CONFIG = {
    "file_requirements": {
        "package_format": "ZIP or TAR.GZ",
        "max_size_mb": 50,
        "main_html": "index.html (必须存在)",
        "supported_formats": [".html", ".js", ".css", ".png", ".jpg", ".mp3", ".ogg", ".wav"]
    },
    "game_config": {
        "title": "游戏名称 (中英文)",
        "description": "游戏描述",
        "icon": "应用图标 512x512 PNG",
        "screenshots": ["截图1", "截图2", "截图3"],
        "category": "休闲/益智/动作/其他",
        "language": "游戏内文字语言"
    },
    "technical_requirements": {
        "max_loading_time": 8,  // 秒
        "min_fps": 30,
        "memory_limit": "150MB",
        "webgl_support": "推荐支持",
        "touch_support": "必须支持"
    }
}


def get_nocode_tool_recommendation(game_type: str) -> str:
    """根据游戏类型推荐零代码工具"""
    recommendations = {
        "跑酷": "Construct 3 - 有丰富的跑酷模板",
        "消除": "Construct 3 - 消除游戏模板丰富",
        "射击": "GDevelop - 开源免费，2D射击功能强",
        "休闲": "Construct 3 或 Buildbox",
        "解谜": "GDevelop - 事件系统灵活",
        "3D": "PlayCanvas - 原生支持TikTok"
    }
    return recommendations.get(game_type, "Construct 3 - 综合最推荐")


def generate_game_requirements() -> dict:
    """生成游戏需求文档模板"""
    return {
        "basic_info": {
            "game_name": "",
            "game_type": "",
            "target_audience": "",
            "game_description": ""
        },
        "visual_style": {
            "art_style": "像素/卡通/写实/简约",
            "color_scheme": "",
            "ui_style": ""
        },
        "gameplay": {
            "core_mechanics": "",
            "difficulty_curve": "",
            "play_session_length": "3-5分钟"
        },
        "monetization": {
            "ad_placement": ["激励视频复活", "关卡间插屏", "Banner"],
            "reward_timing": ""
        },
        "technical": {
            "engine": "",
            "export_platform": ["TikTok Mini Game"],
            "performance_target": "30FPS"
        }
    }


def main():
    """主函数"""
    print("=" * 60)
    print("TikTok Mini Game Generator")
    print("TikTok小游戏生成器")
    print("=" * 60)
    print()

    print("推荐零代码游戏制作工具:")
    print("-" * 40)
    for key, tool in NOCODE_TOOLS.items():
        print(f"{tool['name']}")
        print(f"  描述: {tool['description']}")
        print(f"  价格: {tool['pricing']}")
        print(f"  导出: {', '.join(tool['export_targets'])}")
        print()

    print("=" * 60)
    print("快速游戏模板:")
    print("-" * 40)
    print("简化版Flappy Bird游戏代码已准备好")
    print("保存在: scripts/game_generator.py")
    print()

    print("TikTok导出要求:")
    print("-" * 40)
    for key, value in TIKTOK_EXPORT_CONFIG["file_requirements"].items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
