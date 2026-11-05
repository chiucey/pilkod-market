# Skill 安全审计模式库

## 一、凭证泄露检测模式

### 硬编码密码
```regex
password\s*[=:]\s*["'][^"']{4,}["']
passwd\s*[=:]\s*["'][^"']{4,}["']
```

### API密钥
```regex
api[_-]?key\s*[=:]\s*["'][^"']{10,}["']
secret[_-]?key\s*[=:]\s*["'][^"']{10,}["']
access[_-]?token\s*[=:]\s*["'][^"']{10,}["']
```

### 私钥文件
```regex
-----BEGIN.*PRIVATE KEY-----
ssh-rsa\s+AAAA
```

## 二、路径安全检测

### 路径遍历
```regex
\.\./|\.\.\\\\|%\.\.%|/\.\./
```

### 敏感路径访问
```regex
/etc/passwd
/etc/shadow
~/.ssh/
/root/\.ssh/
```

## 三、命令执行检测

### 危险命令
```regex
rm\s+-rf\s+
dd\s+
mkfs\s+
format\s+[a-z]:
:wq!\s
```

### Shell执行
```regex
eval\s*\(
exec\s*\(
system\s*\(
bash\s+-c
sh\s+-c
```

## 四、网络安全检测

### 外部请求模式
```regex
curl\s+.*http
wget\s+.*
requests\.get\s*\(
fetch\s*\(
```

### 可疑URL
```regex
\.ru\/|\.cn\/|bit\.ly\/|t\.co\/
```

## 五、内容安全检测

### 钓鱼模式
```regex
点击此处|立即获取|限时免费
您的账户已被冻结
```

### 恶意诱导
```regex
稳赚不赔|保证收益|内部消息
```

## 六、代码执行风险

### 代码注入
```regex
exec\s*\(.*\+|eval\s*\(.*\+
compile\s*\(.*\+|__import__
```

### 序列化风险
```regex
pickle\.load|pickle\.loads
yaml\.load\s*\(.*Loader\s*=\s*yaml\.FullLoader
```

## 七、检查清单

### 必检项（高危）
- [ ] SKILL.md存在性
- [ ] _meta.json格式
- [ ] 硬编码凭证
- [ ] 路径遍历风险
- [ ] 命令执行风险

### 建议检项（中危）
- [ ] 外部网络请求
- [ ] 文件系统权限
- [ ] 超时配置
- [ ] 输入验证

### 优化项（低危）
- [ ] 风险提示完整性
- [ ] 错误处理
- [ ] 文档完整性
