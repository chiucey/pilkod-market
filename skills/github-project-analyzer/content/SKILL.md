---
name: github-project-analyzer
description: Analyze and read GitHub repositories. Use when users ask to analyze, inspect, or read GitHub projects, including repository structure, code analysis, dependency examination, or understanding project architecture. Triggers include phrases like "analyze GitHub project", "read GitHub repo", "inspect repository", "check GitHub code", "understand project structure".
---

# GitHub Project Analyzer

Analyzes GitHub repositories by extracting and examining repository metadata, file structure, code content, and technical details.

## Workflow

### Step 1: Identify Repository

Parse the GitHub URL or repository identifier from user input:
- Full URL: `https://github.com/owner/repo` or `github.com/owner/repo`
- Short format: `owner/repo`
- Extract: `owner`, `repo_name`

### Step 2: Gather Repository Metadata

Fetch repository information using web search and content extraction:

1. **Repository Main Page** (`https://github.com/{owner}/{repo}`)
   - Description, stars, forks, watchers, language
   - Topics/tags, license, README preview
   - Last commit date, activity status

2. **Repository Insights** (`https://github.com/{owner}/{repo}/ insights`)
   - Traffic data, popular content
   - Activity graphs

3. **Repository Releases** (`https://github.com/{owner}/{repo}/releases`)
   - Version history, latest release notes
   - Release dates and changelogs

### Step 3: Analyze Project Structure

Extract and analyze file listings:

1. **File Tree** (`https://github.com/{owner}/{repo}/find/main`)
   - Directory structure overview
   - Key configuration files (package.json, requirements.txt, Cargo.toml, etc.)

2. **Key Files Content**:
   - `README.md` - Project documentation and usage
   - `package.json` / `requirements.txt` / `Cargo.toml` / `go.mod` - Dependencies
   - `.github/workflows/*.yml` - CI/CD pipelines
   - `LICENSE` - License information
   - `CONTRIBUTING.md` - Contribution guidelines

### Step 4: Code Analysis (Optional)

For deeper analysis, examine source files:
- Main entry points (`index.js`, `main.py`, `main.go`, etc.)
- Core module files
- Test files to understand testing approach
- Build configuration files

### Step 5: Generate Analysis Report

Compile findings into structured report:

```markdown
## Repository Overview
- **Name**: [repo_name]
- **Owner**: [owner]
- **Description**: [description]
- **Language**: [primary language]
- **Stars**: [count] | **Forks**: [count]
- **License**: [license type]
- **Last Updated**: [date]

## Project Structure
- [Directory tree or key files]

## Technical Stack
- [Languages, frameworks, key libraries]

## Dependencies
- [Key dependencies from package files]

## CI/CD Pipeline
- [Workflow files and their purposes]

## Key Features
- [From README and code analysis]

## Activity & Maintenance
- [Release frequency, commit activity, community engagement]
```

## Output Format

Present analysis in clear markdown with:
- Structured sections with headers
- Bullet points for lists
- Code blocks for technical details
- Tables for comparative data (dependencies, versions)

## Tools

- `batch_web_search`: Find repository URLs, related projects, community discussions
- `extract_content_from_websites`: Fetch repository pages and file content
- `mcp__matrix__bash`: Run local analysis commands if repository is cloned

## Examples

**User Input**: "Analyze https://github.com/facebook/react"

**Analysis Steps**:
1. Extract owner=facebook, repo=react
2. Fetch main page for metadata (stars ~220k, language=JavaScript, etc.)
3. Extract README for feature overview
4. Analyze package.json for dependencies (React, Flow, etc.)
5. Check .github/workflows for CI/CD setup
6. Generate comprehensive report

**User Input**: "Read the project structure of microsoft/vscode"

**Analysis Steps**:
1. Extract owner=microsoft, repo=vscode
2. Fetch file tree to understand directory structure
3. Identify key directories (src/, extensions/, etc.)
4. Examine main configuration files
5. Present structure overview with descriptions

## Notes

- For private repositories, inform user that public analysis is limited
- Respect rate limits by batching requests when possible
- Focus on user-specified aspects (structure, dependencies, or general overview)
- Use GitHub's raw content URLs for direct file access when needed
