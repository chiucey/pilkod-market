# 微信读书 Key 配置引导

仅在检测不到 `WEREAD_API_KEY`，或用户已经把 Key 发进普通对话时读取本文件。

## 必须先说清楚

整个过程有两次粘贴：

1. 第一次：把下面的整段配置命令粘贴到系统终端。
2. 第二次：终端出现“请在最右边的冒号后粘贴 Key”后，再粘贴真正的微信读书 Key。

第二次粘贴时，Key 不会显示，屏幕上也不会出现星号。这是正常的。

位置示意：

```text
请在这行最右边的冒号后粘贴微信读书 Key（粘贴内容不会显示）: ******
```

`******` 只是位置示意。真实操作时，直接在冒号后粘贴 Key，然后按回车。

MiniMax 只展示引导，不代替用户执行命令，不查看终端结果中的 Key。

## macOS

告诉用户按下面顺序操作：

1. 按 `Command + 空格`，搜索并打开苹果电脑自带的“终端”。
2. 完整复制下面代码框中的所有内容。
3. 粘贴到终端，按一次回车。
4. 终端出现下面这句话后：

   ```text
   请在这行最右边的冒号后粘贴微信读书 Key（粘贴内容不会显示）:
   ```

5. 把真正的 Key 粘贴在冒号后面，再按一次回车。粘贴后屏幕没有变化也要按回车。
6. 看到“已保存”后，按 `Command + Q` 完全退出 MiniMax Code，再重新打开。
7. 回到新对话回复“已配置”。

用户需要复制的完整命令：

```zsh
read -s "WEREAD_API_KEY?请在这行最右边的冒号后粘贴微信读书 Key（粘贴内容不会显示）: "
echo
if [[ "$WEREAD_API_KEY" == wrk-* ]]; then
  printf '\nexport WEREAD_API_KEY=%q\n' "$WEREAD_API_KEY" >> "$HOME/.zshrc"
  launchctl setenv WEREAD_API_KEY "$WEREAD_API_KEY"
  echo "已保存。请完全退出并重新打开 MiniMax Code。"
else
  echo "Key 格式不正确，请重新运行这段命令。"
fi
unset WEREAD_API_KEY
```

这段命令不会把真正的 Key 写入终端历史。它会保存到当前用户的 shell 配置，并让重新打开的 MiniMax Code 读取。

## Windows

告诉用户按下面顺序操作：

1. 打开开始菜单，搜索并打开 `PowerShell`。
2. 完整复制下面代码框中的所有内容。
3. 粘贴到 PowerShell，按一次回车。
4. PowerShell 出现下面这句话后：

   ```text
   请在这行最右边的冒号后粘贴微信读书 Key（粘贴内容不会显示）:
   ```

5. 把真正的 Key 粘贴在冒号后面，再按一次回车。粘贴后屏幕没有变化也要按回车。
6. 看到“已保存”后，完全退出 MiniMax Code，再重新打开。
7. 回到新对话回复“已配置”。

用户需要复制的完整命令：

```powershell
$SecureKey = Read-Host "请在这行最右边的冒号后粘贴微信读书 Key（粘贴内容不会显示）" -AsSecureString
$Pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureKey)
try {
  $PlainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Pointer)
  if ($PlainKey -like "wrk-*") {
    [Environment]::SetEnvironmentVariable("WEREAD_API_KEY", $PlainKey, "User")
    Write-Host "已保存。请完全退出并重新打开 MiniMax Code。"
  } else {
    Write-Host "Key 格式不正确，请重新运行这段命令。"
  }
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Pointer)
  Remove-Variable PlainKey, SecureKey -ErrorAction SilentlyContinue
}
```

## 重启后的检查

用户回复“已配置”后，只运行：

```bash
python3 scripts/weread_key.py status
```

- 返回 `READY`：使用 `scripts/weread_gateway.py` 调用 `/_list`。
- 返回 `MISSING`：提醒用户确认 MiniMax Code 已经完全退出并重新打开。不要读取 `.zshrc`、PowerShell 配置或系统环境变量内容进行排查。

## 用户已经把 Key 发进对话

不要使用消息里的值，也不要复述。回复：

> 这枚 Key 已经进入聊天记录，建议先到[微信读书设置页](https://weread.qq.com/setting)重新生成。新 Key 不要发到对话里，请按照上面的终端步骤配置。
