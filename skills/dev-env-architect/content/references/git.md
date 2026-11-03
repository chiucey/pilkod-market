---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100f7fc352b87db50ac69c635f9e782d9c8eda1e0af0cda2eb009f97b83814270eb022031b76671fd5e86a87452e4616dfb69f7263e98d1c6457952f5480112b3cbf981
    ReservedCode2: 30440220360686329c9ed788f55076ca28cdb30a03a1d58c0abdfeba267bac3e63849cc402204951987812edafdc1ffc0f3b386f4931d40cd53d0d6bba6aa7809ad72b6fdef8
---

# Git Version Control Reference

## Overview
Git is a distributed version control system essential for modern software development, enabling code tracking, collaboration, and history management <citation>41</citation>.

## Workflows Comparison

### Git Flow
Suitable for projects with long release cycles and larger teams <citation>47</citation>

```
main (production) ─────────────────┐
    ↑                              │
release/* (preparation) ←──────────┘
    ↑
develop (integration) ←────────────┐
    ↑                    ↑         │
feature/* ──────────>──┘   hotfix/* → (emergency fixes)
```

**Branches:**
- `main`: Production-ready code
- `develop`: Latest development changes
- `feature/*`: New feature development
- `release/*`: Release preparation
- `hotfix/*`: Production emergency fixes

### GitHub Flow
Suitable for continuous deployment and rapid iteration <citation>48</citation>

```
main ────→ feature/* ────→ PR ────→ main ────→ deploy
```

**Rules:**
- `main` is always deployable
- Work on feature branches
- Use Pull Requests for code review
- Merge after review approval

### GitLab Flow
Combines feature branches with environment branches

```
production ← staging ← main ← feature/*
```

## Essential Commands

### Setup & Configuration
```bash
# Global configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Line ending configuration (Windows)
git config --global core.autocrlf true

# Line ending configuration (macOS/Linux)
git config --global core.autocrlf input

# Default branch name
git config --global init.defaultBranch main

# Aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.lg "log --oneline --graph --decorate"
```

### Basic Operations
```bash
# Initialize repository
git init
git init --initial-branch=main

# Clone repository
git clone https://github.com/user/repo.git
git clone --depth 1 https://github.com/user/repo.git  # Shallow clone

# Add and commit
git add file.txt           # Stage specific file
git add .                  # Stage all changes
git add -p                 # Interactive staging
git commit -m "message"
git commit -am "message"   # Add and commit tracked files

# Push and pull
git push origin main
git push -u origin feature  # Set upstream
git pull origin main
git pull --rebase           # Rebase on pull
```

### Branching
```bash
# Create and switch
git branch feature-name
git checkout feature-name
git switch -c feature-name  # Modern way

# List branches
git branch                 # Local
git branch -a              # All (including remote)
git branch -vv             # Detailed with tracking

# Delete
git branch -d feature-name      # Safe delete
git branch -D feature-name      # Force delete
git push origin --delete feature # Remote delete

# Rename
git branch -m old-name new-name
```

### Merging & Rebasing
```bash
# Merge
git checkout main
git merge feature-name
git merge --no-ff feature   # No fast-forward

# Rebase (interactive)
git rebase -i HEAD~3       # Last 3 commits

# Resolve conflicts
git mergetool              # Use merge tool
git add resolved-file.txt
git rebase --continue
git rebase --abort          # Cancel rebase
```

## Commit Message Conventions

### Conventional Commits
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(auth): add JWT authentication
fix(api): resolve CORS issue
docs(readme): update installation guide
refactor(core): extract utility functions
```

### Commit Message Rules
- Use imperative mood ("add" not "added")
- First line under 50 characters
- Body wrapped at 72 characters
- Reference issues: `Closes #123`

## .gitignore Best Practices

### Common Patterns
```
# Dependencies
node_modules/
.pnp/
.pnp.js

# Build outputs
dist/
build/
*.o
*.pyc

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
.env.*.local

# Logs
*.log
npm-debug.log*

# OS
.DS_Store
Thumbs.db

# Testing
coverage/
.nyc_output/
```

### Template
```bash
# Use GitHub templates
curl https://raw.githubusercontent.com/github/gitignore/main/Node.gitignore -o .gitignore
```

## Git Hooks

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run linter
npm run lint
if [ $? -ne 0 ]; then
  echo "Linting failed"
  exit 1
fi

# Run tests
npm test
if [ $? -ne 0 ]; then
  echo "Tests failed"
  exit 1
fi
```

### Commit-msg Hook
```bash
#!/bin/bash
# .git/hooks/commit-msg

commit_msg=$(cat "$1")
pattern="^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}"

if ! [[ $commit_msg =~ $pattern ]]; then
  echo "Invalid commit message format"
  exit 1
fi
```

## GitHub Actions Integration

### CI Workflow
```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm test
```

### GitHub Flow Deployment
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run build
      - run: npm run deploy
```

## Advanced Operations

### Stashing
```bash
git stash                    # Stash changes
git stash pop               # Apply and remove stash
git stash list              # List stashes
git stash apply stash@{0}   # Apply specific stash
git stash -u                # Include untracked files
git stash -p                # Interactive stash
```

### Searching
```bash
git log --author="name"           # By author
git log --since="2024-01-01"      # By date
git log --grep="keyword"          # In messages
git log -S "code pattern"          # In code changes
git log --oneline --all --graph    # Visual history
```

### Reset & Restore
```bash
git restore file.txt         # Discard changes
git restore --staged file.txt  # Unstage
git reset HEAD~1             # Undo last commit
git reset --hard HEAD~1      # Hard reset
```

## Collaboration

### Forking Workflow
```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/your-username/repo.git
cd repo

# Add upstream remote
git remote add upstream https://github.com/original/repo.git

# Keep fork updated
git fetch upstream
git merge upstream/main
git push origin main
```

### Pull Requests
```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git commit -m "feat: add my feature"

# Push and create PR
git push -u origin feature/my-feature
```

## Security

### Signed Commits
```bash
# Generate GPG key
gpg --full-generate-key

# List keys
gpg --list-secret-keys

# Configure Git
git config --global user.signingkey YOUR_KEY_ID
git config --global commit.gpgsign true

# Sign tags
git tag -s v1.0.0 -m "Version 1.0.0"
git push --tags
```

## Performance

### Shallow Clone for CI
```bash
git clone --depth 1 --single-branch https://github.com/user/repo.git
```

### Optimize Repository
```bash
git gc                    # Garbage collection
git prune                 # Remove unreachable objects
git fsck                  # Verify repository
```

## Additional Resources
- Pro Git Book: https://git-scm.com/book
- GitHub Learning Lab: https://lab.github.com/
- Oh Shit, Git: https://ohshitgit.com/
