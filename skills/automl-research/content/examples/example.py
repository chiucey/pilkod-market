#!/usr/bin/env python3
"""
AutoML Research - 使用示例
展示如何使用 automl-research 技能进行自动机器学习实验
"""

import os
import sys
import subprocess
import shutil

# 假设这是 nanobot 的调用方式
def run_automl_research(
    data_path: str,
    target_col: str,
    task_type: str = 'classification',
    metric: str = None,
    time_budget: int = 120,
    max_experiments: int = 50,
    workspace: str = './automl_exp'
):
    """
    运行 AutoML Research 实验

    参数:
        data_path: 数据文件路径
        target_col: 目标列名
        task_type: 任务类型 (classification/regression/multiclass)
        metric: 评估指标（None 则自动选择）
        time_budget: 每轮训练时间预算（秒）
        max_experiments: 最大实验轮数
        workspace: 工作目录
    """

    # 设置环境变量
    env = os.environ.copy()
    env['AUTOML_DATA'] = data_path
    env['AUTOML_TARGET'] = target_col
    env['AUTOML_TASK'] = task_type
    env['AUTOML_METRIC'] = metric or get_default_metric(task_type)
    env['AUTOML_TIME_BUDGET'] = str(time_budget)
    env['AUTOML_MAX_EXPERIMENTS'] = str(max_experiments)
    env['AUTOML_WORKSPACE'] = workspace

    print("=" * 60)
    print("AutoML Research 实验启动")
    print("=" * 60)
    print(f"数据路径: {data_path}")
    print(f"目标列: {target_col}")
    print(f"任务类型: {task_type}")
    print(f"评估指标: {env['AUTOML_METRIC']}")
    print(f"时间预算: {time_budget} 秒/轮")
    print(f"最大实验数: {max_experiments}")
    print(f"工作目录: {workspace}")
    print("=" * 60)

    # 创建工作目录
    os.makedirs(workspace, exist_ok=True)

    # 检查数据文件
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"数据文件不存在: {data_path}")

    # 复制数据到工作目录（或创建符号链接）
    data_dst = os.path.join(workspace, 'data.csv')
    if not os.path.exists(data_dst):
        shutil.copy(data_path, data_dst)

    # 复制模板文件（如果它们不存在）
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for file in ['prepare.py', 'train.py', 'program.md']:
        src = os.path.join(skill_dir, file)
        dst = os.path.join(workspace, file)
        if not os.path.exists(dst) and os.path.exists(src):
            shutil.copy(src, dst)

    # 初始化 git 仓库（用于实验跟踪）
    if not os.path.exists(os.path.join(workspace, '.git')):
        subprocess.run(['git', 'init'], cwd=workspace, check=True, capture_output=True)
        subprocess.run(['git', 'add', '.'], cwd=workspace, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'initial commit'], cwd=workspace, check=True, capture_output=True)

    # 验证环境
    print("\n验证环境...")
    result = subprocess.run(
        [sys.executable, 'prepare.py', '--check-data'],
        cwd=workspace,
        capture_output=True,
        text=True,
        env=env
    )
    print(result.stdout)
    if result.returncode != 0:
        print("数据验证失败:", result.stderr)
        return

    # 运行 baseline
    print("\n建立 baseline...")
    result = subprocess.run(
        [sys.executable, 'train.py'],
        cwd=workspace,
        capture_output=True,
        text=True,
        env=env,
        timeout=time_budget + 30
    )

    if result.returncode != 0:
        print("Baseline 运行失败:", result.stderr)
        return

    # 解析 baseline 结果
    baseline_results = parse_output(result.stdout)
    print(f"Baseline 结果:")
    for key, value in baseline_results.items():
        print(f"  {key}: {value}")

    # 初始化 results.tsv
    results_file = os.path.join(workspace, 'results.tsv')
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write("commit\tmetric\tmemory_mb\tstatus\tdescription\n")
        f.write(f"baseline\t{baseline_results.get(f'val_{env['AUTOML_METRIC']}', 0):.6f}\t"
                f"{baseline_results.get('memory_mb', 0):.1f}\tkeep\tbaseline\n")

    print(f"\nBaseline 已记录到 {results_file}")
    print("\n准备开始实验循环...")
    print("提示: 现在你可以启动 AI 代理进行自主实验了")

    return baseline_results


def get_default_metric(task_type):
    """获取默认评估指标"""
    metrics = {
        'classification': 'accuracy',
        'multiclass': 'f1_macro',
        'regression': 'rmse'
    }
    return metrics.get(task_type, 'accuracy')


def parse_output(output):
    """解析 train.py 的输出"""
    results = {}
    for line in output.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            try:
                value = float(value)
            except ValueError:
                pass
            results[key] = value
    return results


def analyze_results(workspace='./automl_exp'):
    """分析实验结果"""
    import pandas as pd

    results_file = os.path.join(workspace, 'results.tsv')
    if not os.path.exists(results_file):
        print(f"结果文件不存在: {results_file}")
        return

    df = pd.read_csv(results_file, sep='\t')

    print("\n" + "=" * 60)
    print("实验结果分析")
    print("=" * 60)
    print(f"\n总实验数: {len(df)}")
    print(f"成功实验: {len(df[df['status'] == 'success'])} + {len(df[df['status'] == 'keep'])}")
    print(f"废弃实验: {len(df[df['status'] == 'discard'])}")
    print(f"崩溃实验: {len(df[df['status'] == 'crash'])}")

    # 找出最佳实验
    best_idx = df['metric'].idxmax()
    best = df.loc[best_idx]

    print(f"\n最佳实验:")
    print(f"  Commit: {best['commit']}")
    print(f"  指标: {best['metric']:.6f}")
    print(f"  内存: {best['memory_mb']:.1f} MB")
    print(f"  描述: {best['description']}")

    # 计算提升
    baseline_metric = df[df['commit'] == 'baseline']['metric'].values[0]
    improvement = (best['metric'] - baseline_metric) / baseline_metric * 100

    print(f"\n相比 Baseline:")
    print(f"  指标提升: {improvement:+.2f}%")

    return df


# ========== 示例用法 ==========

if __name__ == '__main__':
    # 示例 1: 二分类任务
    print("示例 1: 二分类任务 - 鸢尾花数据集")
    print("-" * 60)

    # 创建示例数据（实际使用时替换为真实数据）
    from sklearn.datasets import load_iris
    import pandas as pd

    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['species'] = iris.target

    # 转换为二分类问题
    df = df[df['species'] != 2]  # 只保留前两类
    df['species'] = df['species'].map({0: 0, 1: 1})

    # 保存示例数据
    os.makedirs('./example_data', exist_ok=True)
    df.to_csv('./example_data/iris_binary.csv', index=False)

    # 运行 AutoML
    results = run_automl_research(
        data_path='./example_data/iris_binary.csv',
        target_col='species',
        task_type='classification',
        metric='accuracy',
        time_budget=30,  # 30秒/轮
        max_experiments=20,
        workspace='./automl_exp_iris'
    )

    # 示例 2: 回归任务
    print("\n" + "=" * 60)
    print("示例 2: 回归任务 - 波士顿房价")
    print("-" * 60)

    # 创建示例数据
    from sklearn.datasets import fetch_california_housing

    housing = fetch_california_housing()
    df = pd.DataFrame(housing.data, columns=housing.feature_names)
    df['price'] = housing.target

    # 保存示例数据
    df.to_csv('./example_data/california_housing.csv', index=False)

    # 运行 AutoML
    results = run_automl_research(
        data_path='./example_data/california_housing.csv',
        target_col='price',
        task_type='regression',
        metric='rmse',
        time_budget=60,
        max_experiments=30,
        workspace='./automl_exp_housing'
    )
