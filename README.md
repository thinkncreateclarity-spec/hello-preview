**Status:** Prototype. This repository is experimental and may not have CI, tests, or stable APIs yet.
# Ajay's CLI Preview Pipeline 🚀

**Production**: https://web-production-33a3c.up.railway.app/
**Status**: LIVE ✅ PR Environments: ENABLED ✅

## Complete Workflow (Termux → Preview → Production)

```bash
# 1. Feature branch + changes
git checkout -b feature-login
echo '<p>Login feature added</p>' >> hello.py
git add . && git commit -m "feat: add login"

# 2. CLI-ONLY PR creation (GitHub CLI)
gh pr create --title "feat: add login" --body "Login preview"

# 3. MAGIC: Railway auto-deploys PR #X
# https://web-pr-X.up.railway.app/ → "PR #X live on Railway!"

# 4. Merge → Production
gh pr merge --merge --delete-branch

## 🚀 Multi-Service + Database Evolution (Phase 2)

**Status**: Brainstormed → Next: Build FastAPI + Postgres + Frontend

### Case Study: Task Tracker (Todoist Mini)

