# Dota 2 赛后分析

**触发词：上场dota2复盘**

当用户说「上场dota2复盘」「分析我最近一场Dota」「复盘一下」等类似表达时触发此 Skill。

## 工作流程

**第一步：运行检测脚本**
执行命令：
```
python3 /workspace/dota-monitor/checker.py
```

**第二步：检查结果**
- 输出 `NO_NEW_MATCH` → 告诉用户"最近没有新比赛"
- 有新比赛 → 继续第三步

**第三步：运行分析脚本**
执行命令：
```
python3 /workspace/dota-monitor/fetch_and_analyze.py
```

**第四步：发送微信**
检查是否有新的分析文件：
```
ls /workspace/dota-monitor/.queue_*.txt
```

读取每个文件内容，使用 `message` 工具发送：

```
action: send
channel: openclaw-weixin
target: o9cq80wTdq3595N6C9cY9vlXrGYY@im.wechat
message: <文件全部内容>
```

**第五步：删除已发送文件**
```
rm /workspace/dota-monitor/.queue_<match_id>.txt
```

## 注意事项
- 每次手动触发，分析最近有新比赛的那几场
- 发送对象仅为 freyer14（不需要发给其他人）
- 如果没有新比赛，直接告知用户即可
