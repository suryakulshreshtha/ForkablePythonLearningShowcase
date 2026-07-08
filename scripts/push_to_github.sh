#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
#  push_to_github.sh — One-Command GitHub Publisher
#  Repo   : ForkablePythonLearningShowcase
#  Author : Surya Kulshreshtha
#
#  WHAT THIS DOES (in order):
#    1. Safety checks (git installed, right folder, remote not misconfigured)
#    2. git init          — turn this folder into a Git repository
#    3. git add .         — stage every project file
#    4. git commit        — snapshot with a message
#    5. git branch -M main
#    6. git remote add    — link to your GitHub repo
#    7. git push          — upload (Git will ask YOU for username + token)
#
#  SECURITY: This script contains NO password and NO token.
#  When Git asks for a password, paste your Personal Access Token —
#  it goes straight from your keyboard to Git, nowhere else.
#
#  USAGE:
#    cd ForkablePythonLearningShowcase
#    chmod +x push_to_github.sh
#    ./push_to_github.sh
# ═══════════════════════════════════════════════════════════════════════════

set -e   # stop immediately if any command fails

GITHUB_USER="suryakulshreshtha"
REPO_NAME="ForkablePythonLearningShowcase"
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
BRANCH="main"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

step()  { echo -e "\n${GREEN}▶ $1${NC}"; }
warn()  { echo -e "${YELLOW}⚠ $1${NC}"; }
fail()  { echo -e "${RED}✖ $1${NC}"; exit 1; }

# ─── Pre-flight checks ──────────────────────────────────────────────────────

step "STEP 0: Pre-flight safety checks"

command -v git >/dev/null 2>&1 || fail "Git is not installed. Install from https://git-scm.com and re-run."

# This script lives in scripts/ — hop up to the project root automatically.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${SCRIPT_DIR}/.." || fail "Could not locate the project root from ${SCRIPT_DIR}"

[ -f "pytest.ini" ] && [ -f "conftest.py" ] \
  || fail "Project root not found. Run this script from inside the ${REPO_NAME} repo."

if ! git config --global user.name >/dev/null 2>&1; then
  warn "Git doesn't know who you are yet. Setting it up now..."
  read -rp "  Enter your name (e.g. Surya Kulshreshtha): " GIT_NAME
  read -rp "  Enter your GitHub email: " GIT_EMAIL
  git config --global user.name  "$GIT_NAME"
  git config --global user.email "$GIT_EMAIL"
fi
echo "  Git identity : $(git config --global user.name) <$(git config --global user.email)>"

echo ""
warn "BEFORE CONTINUING — the empty repo must already exist on GitHub:"
echo "    1. Open  https://github.com/new"
echo "    2. Repository name :  ${REPO_NAME}"
echo "    3. Visibility      :  Public"
echo "    4. Leave 'Add a README' UNCHECKED (must be completely empty)"
echo "    5. Click 'Create repository'"
echo ""
read -rp "Have you created the empty repo '${REPO_NAME}' on GitHub? (y/n): " CONFIRM
[ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ] || fail "Create the repo first, then re-run this script."

# ─── Git operations ─────────────────────────────────────────────────────────

step "STEP 1: Initialise Git repository (git init)"
if [ -d ".git" ]; then
  echo "  Already a Git repo — skipping init."
else
  git init
fi

step "STEP 2: Stage all files (git add .)"
git add .
echo "  Files staged: $(git diff --cached --numstat | wc -l | tr -d ' ')"

step "STEP 3: Commit snapshot (git commit)"
if git diff --cached --quiet; then
  echo "  Nothing new to commit — skipping."
else
  git commit -m "Initial commit: Playwright + pytest automation framework (62 tests, POM, CI/CD)"
fi

step "STEP 4: Rename branch to ${BRANCH} (git branch -M ${BRANCH})"
git branch -M "$BRANCH"

step "STEP 5: Link to GitHub (git remote add origin)"
if git remote get-url origin >/dev/null 2>&1; then
  EXISTING=$(git remote get-url origin)
  if [ "$EXISTING" != "$REPO_URL" ]; then
    warn "Remote 'origin' points to: $EXISTING"
    read -rp "  Replace it with ${REPO_URL}? (y/n): " REPLACE
    [ "$REPLACE" = "y" ] && git remote set-url origin "$REPO_URL" || fail "Aborted — remote left unchanged."
  else
    echo "  Remote already correct."
  fi
else
  git remote add origin "$REPO_URL"
fi
echo "  origin → $(git remote get-url origin)"

step "STEP 6: Push to GitHub (git push -u origin ${BRANCH})"
echo ""
warn "Git will now ask for credentials:"
echo "    Username : ${GITHUB_USER}"
echo "    Password : paste your Personal Access Token (NOT your GitHub password)"
echo "    Need a token? → GitHub → Settings → Developer settings → Tokens (classic)"
echo "                     → Generate new token → tick 'repo' + 'workflow' scopes"
echo ""
git push -u origin "$BRANCH"

# ─── Done ────────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ SUCCESS — your project is live!${NC}"
echo -e "${GREEN}  https://github.com/${GITHUB_USER}/${REPO_NAME}${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  NEXT STEPS:"
echo "  1. Open the repo — README renders automatically"
echo "  2. Add CI secret: Settings → Secrets and variables → Actions"
echo "     → New repository secret → Name: TEST_PASSWORD → Value: SuperSecretPassword!"
echo "  3. Check the Actions tab — CI runs on your next push"
