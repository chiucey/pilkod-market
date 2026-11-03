---
name: local-command-executor
description: Execute basic system commands in a local environment. Use when users request commands like cat, pwd, env, ls, echo, grep, find, ps, whoami, or other shell commands.
---

# Local Command Executor

This skill enables safe execution of local system commands in a sandbox environment.

## Core Capabilities

- **File System Operations**: `cat`, `ls`, `pwd`, `cd`, `find`, `grep`
- **Environment Info**: `env`, `whoami`, `uname`, `hostname`
- **Text Processing**: `echo`, `head`, `tail`, `wc`, `sort`, `uniq`
- **Process Management**: `ps`, `top`, `kill`, `pgrep`
- **Network Diagnostics**: `ping`, `curl`, `wget`, `netstat`

## Execution Principles

### Security Boundaries
1. **Read-only first**: Use `cat`, `ls`, `grep` and other read-only commands for information gathering
2. **Explicit risk assessment**: Evaluate risk level before executing modifying commands
3. **User confirmation**: Require confirmation for destructive operations (delete, overwrite)

### Command Classification

#### Low Risk (Execute Directly)
- Read-only commands: `cat`, `pwd`, `ls`, `env`, `whoami`, `uname`
- Information queries: `ps`, `df`, `du`, `free`, `top`
- Network diagnostics: `ping`, `curl`, `traceroute`

#### Medium Risk (Require User Intent)
- File creation/edit: `touch`, `mkdir`, `cp`, `mv`
- Text writing: `echo >`, `tee`
- Permission changes: `chmod`, `chown`

#### High Risk (Require Explicit Confirmation)
- Delete operations: `rm`, `rmdir`
- System modifications: `apt`, `yum`, `npm install`
- Service management: `systemctl`, `service`

## Execution Flow

### 1. Command Parsing
- Identify the command type from user request
- Evaluate risk level
- Determine if user confirmation is needed

### 2. Risk Assessment
```python
if is_read_only_command(command):
    return "low"
elif is_destructive_command(command):
    return "high"
else:
    return "medium"
```

### 3. Execution and Response
- Use `mcp__matrix__bash` tool to execute commands
- Limit execution time (default 120 seconds)
- Return command output or error information

## Error Handling

| Error Type | Handling |
|------------|----------|
| Command not found | Return "command not found" with alternative suggestions |
| Permission denied | Explain permission issue, suggest using `sudo` |
| Execution timeout | Return timeout info, ask if user wants to retry |
| Path not found | Provide correct path format suggestions |

## Usage Examples

### Example 1: Show Current Directory
```
User: Show current working directory
Execute: pwd
Output: /workspace
```

### Example 2: View File Content
```
User: Read contents of /workspace/test.txt
Execute: cat /workspace/test.txt
Output: [file content]
```

### Example 3: View Environment Variables
```
User: Display all environment variables
Execute: env
Output: [environment variable list]
```

### Example 4: List Directory Contents
```
User: List files in /workspace directory
Execute: ls -la /workspace
Output: [directory listing]
```

## Notes

1. **Avoid over-execution**: Do not run multiple unrelated commands consecutively
2. **Keep it concise**: Only return results the user needs
3. **Be user-friendly**: Help users understand and fix issues
4. **Timeout protection**: Set timeout for long-running commands

## Limitations

- Cannot execute commands requiring interactive input (e.g., `vim`, `nano`)
- Cannot execute commands requiring GUI
- Cannot execute commands requiring admin privileges without `sudo`
- Command execution environment is temporary sandbox, state is not persistent