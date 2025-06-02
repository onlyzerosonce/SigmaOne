@echo off
setlocal

REM --- Configuration ---
set PYTHON_EXE=python
set PIP_EXE=pip
set REPO_URL="https://github.com/onlyzerosonce/SigmaOne"
set LOCAL_REPO_PATH="."
set OLLAMA_API_ENDPOINT="http://localhost:11434"
set REQUIRED_PACKAGES=PyQt5 GitPython requests

REM --- Helper function to check if a command exists ---
:check_command
where %1 >nul 2>nul
if %errorlevel% equ 0 (
    exit /b 0
) else (
    exit /b 1
)

REM --- 1. Check for Python ---
echo Checking for Python...
call :check_command %PYTHON_EXE%
if %errorlevel% neq 0 (
    echo Python is not found in PATH.
    echo Please install Python from https://www.python.org/downloads/ and ensure it's added to your PATH.
    goto :error_exit
)
echo Python found.

REM --- 2. Check for Pip ---
echo Checking for Pip...
call :check_command %PIP_EXE%
if %errorlevel% neq 0 (
    echo Pip is not found.
    echo Attempting to ensure pip is installed/updated with Python...
    %PYTHON_EXE% -m ensurepip --upgrade
    call :check_command %PIP_EXE%
    if %errorlevel% neq 0 (
      echo Failed to install Pip. Please ensure your Python installation is correct.
      goto :error_exit
    )
)
echo Pip found.

REM --- 3. Install/Upgrade Python dependencies ---
echo Checking and installing Python packages: %REQUIRED_PACKAGES%...
for %%p in (%REQUIRED_PACKAGES%) do (
    echo Installing/updating %%p...
    %PIP_EXE% install --upgrade %%p
    if errorlevel 1 (
        echo Failed to install %%p. Please check your Python/pip setup and internet connection.
        goto :error_exit
    )
)
echo All required Python packages are installed/updated.

REM --- 4. Check for Ollama ---
echo Checking for Ollama service at %OLLAMA_API_ENDPOINT%...
REM Using curl if available (common on modern Windows), otherwise a simple ping-like check for the port might be too complex for batch.
REM For simplicity, we'll use powershell's Test-NetConnection if available, or just inform the user.
powershell -Command "if (Test-NetConnection -ComputerName localhost -Port 11434 -WarningAction SilentlyContinue | Select-Object -ExpandProperty TcpTestSucceeded) { exit 0 } else { exit 1 }"
if errorlevel 1 (
    echo Ollama service not detected at %OLLAMA_API_ENDPOINT%.
    echo Please ensure Ollama is installed and running.
    echo You can download Ollama from https://ollama.com/
    echo The agent may not function correctly without Ollama.
    echo Continuing to start the agent, but chatbot features will likely be disabled.
    echo.
) else (
    echo Ollama service detected.
)


REM --- 5. Git Repository Update ---
echo Checking for application updates...
if not exist "%LOCAL_REPO_PATH%\.git" (
    echo Local repository not found. Cloning from %REPO_URL%...
    git clone %REPO_URL% "%LOCAL_REPO_PATH%"
    if errorlevel 1 (
        echo Failed to clone repository. Please check your internet connection and Git installation.
        goto :error_exit
    )
    echo Repository cloned successfully.
) else (
    echo Local repository found. Fetching updates...
    cd "%LOCAL_REPO_PATH%"
    git fetch origin
    if errorlevel 1 (
        echo Failed to fetch updates. Please check your internet connection.
        REM Continue, as the app can still run with local version
    ) else (
        REM Check if local is behind remote (main or master branch)
        git rev-parse @ > .git\local_commit.txt
        git rev-parse @{u} > .gitemote_commit.txt
        fc .git\local_commit.txt .gitemote_commit.txt > nul
        if errorlevel 1 (
            echo Update available. Pulling changes...
            git pull origin
            if errorlevel 1 (
                echo Failed to pull updates. You might need to resolve conflicts manually.
            ) else (
                echo Application updated successfully.
            )
        ) else (
            echo Application is up to date.
        )
        del .git\local_commit.txt .gitemote_commit.txt 2>nul
        cd ..
    )
)

REM --- 6. Run the application ---
echo Starting General Purpose Agent...
%PYTHON_EXE% "%LOCAL_REPO_PATH%\main.py"

echo Application finished.
goto :end

:error_exit
echo An error occurred during setup. Please check the messages above.
:end
pause
endlocal
