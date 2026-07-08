@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM  push_to_github.bat — One-Command GitHub Publisher (Windows)
REM  Repo   : ForkablePythonLearningShowcase
REM  Author : Surya Kulshreshtha
REM
REM  SECURITY: This script contains NO password and NO token.
REM  When Git asks for a password, paste your Personal Access Token —
REM  it goes straight from your keyboard to Git, nowhere else.
REM
REM  USAGE:  double-click this file, or run in Command Prompt:
REM          push_to_github.bat
REM ═══════════════════════════════════════════════════════════════════════

setlocal
set GITHUB_USER=suryakulshreshtha
set REPO_NAME=ForkablePythonLearningShowcase
set REPO_URL=https://github.com/%GITHUB_USER%/%REPO_NAME%.git
set BRANCH=main

echo.
echo ==== STEP 0: Pre-flight safety checks ====

where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed. Download from https://git-scm.com/download/win
    pause & exit /b 1
)

if not exist "pytest.ini" (
    echo [ERROR] You are not inside the project folder.
    echo         Open Command Prompt inside %REPO_NAME% and re-run.
    pause & exit /b 1
)

git config --global user.name >nul 2>&1
if errorlevel 1 (
    echo Git doesn't know who you are yet.
    set /p GIT_NAME="  Enter your name: "
    set /p GIT_EMAIL="  Enter your GitHub email: "
    git config --global user.name "%GIT_NAME%"
    git config --global user.email "%GIT_EMAIL%"
)

echo.
echo  BEFORE CONTINUING - the empty repo must already exist on GitHub:
echo    1. Open  https://github.com/new
echo    2. Repository name :  %REPO_NAME%
echo    3. Visibility      :  Public
echo    4. Leave 'Add a README' UNCHECKED (must be completely empty)
echo    5. Click 'Create repository'
echo.
set /p CONFIRM="Have you created the empty repo '%REPO_NAME%' on GitHub? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Create the repo first, then re-run this script.
    pause & exit /b 1
)

echo.
echo ==== STEP 1: Initialise Git repository ====
if exist ".git" (
    echo   Already a Git repo - skipping init.
) else (
    git init
)

echo.
echo ==== STEP 2: Stage all files ====
git add .

echo.
echo ==== STEP 3: Commit snapshot ====
git commit -m "Initial commit: Playwright + pytest automation framework (62 tests, POM, CI/CD)"

echo.
echo ==== STEP 4: Rename branch to %BRANCH% ====
git branch -M %BRANCH%

echo.
echo ==== STEP 5: Link to GitHub ====
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    git remote add origin %REPO_URL%
) else (
    echo   Remote 'origin' already exists - updating URL.
    git remote set-url origin %REPO_URL%
)

echo.
echo ==== STEP 6: Push to GitHub ====
echo.
echo   Git will now ask for credentials:
echo     Username : %GITHUB_USER%
echo     Password : paste your Personal Access Token (NOT your GitHub password)
echo     Need a token? GitHub - Settings - Developer settings - Tokens (classic)
echo                   Generate new token - tick 'repo' + 'workflow' scopes
echo.
git push -u origin %BRANCH%
if errorlevel 1 (
    echo.
    echo [ERROR] Push failed. Common causes:
    echo   - Repo not created on GitHub yet
    echo   - Wrong token or missing 'repo' scope
    echo   - Repo was created WITH a README (must be empty)
    pause & exit /b 1
)

echo.
echo ============================================================
echo   SUCCESS - your project is live!
echo   https://github.com/%GITHUB_USER%/%REPO_NAME%
echo ============================================================
echo.
echo   NEXT STEPS:
echo   1. Open the repo - README renders automatically
echo   2. Add CI secret: Settings - Secrets and variables - Actions
echo      New repository secret - Name: TEST_PASSWORD - Value: SuperSecretPassword!
echo   3. Check the Actions tab - CI runs on your next push
echo.
pause
