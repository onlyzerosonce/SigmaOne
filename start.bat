@echo ON
echo Script starting...
pause

setlocal
echo Executing setlocal...
pause

REM --- Configuration ---
set PYTHON_EXE=python
set PIP_EXE=pip
set REPO_URL="https://github.com/onlyzerosonce/SigmaOne"
set LOCAL_REPO_PATH="."
set OLLAMA_API_ENDPOINT="http://localhost:11434"
set REQUIRED_PACKAGES=PyQt5 GitPython requests
echo Configuration set.
pause

REM --- Helper function to check if a command exists ---
:check_command
echo Checking command: %1
where %1 >nul 2>nul
if %errorlevel% equ 0 (
    echo Command %1 found.
    exit /b 0
) else (
    echo Command %1 NOT found.
    exit /b 1
)

REM --- 1. Check for Python ---
echo --- Checking for Python ---
call :check_command %PYTHON_EXE%
if %errorlevel% neq 0 (
    echo ERROR: Python is not found in PATH.
    echo Please install Python from https://www.python.org/downloads/ and ensure it's added to your PATH.
    goto :error_exit
)
echo Python check successful.
pause

REM --- 2. Check for Pip ---
echo --- Checking for Pip ---
call :check_command %PIP_EXE%
if %errorlevel% neq 0 (
    echo WARNING: Pip is not found.
    echo Attempting to ensure pip is installed/updated with Python...
    %PYTHON_EXE% -m ensurepip --upgrade
    call :check_command %PIP_EXE%
    if %errorlevel% neq 0 (
      echo ERROR: Failed to install Pip. Please ensure your Python installation is correct.
      goto :error_exit
    )
)
echo Pip check successful.
pause

REM --- 3. Install/Upgrade Python dependencies ---
echo --- Checking and installing Python packages: %REQUIRED_PACKAGES% ---
for %%p in (%REQUIRED_PACKAGES%) do (
    echo Installing/updating %%p...
    %PIP_EXE% install --upgrade %%p
    if errorlevel 1 (
        echo ERROR: Failed to install %%p. Please check your Python/pip setup and internet connection.
        echo Errorlevel: %errorlevel%
        goto :error_exit
    )
    echo %%p installed/updated successfully.
)
echo All required Python packages are installed/updated.
pause

REM --- 4. Check for Ollama ---
echo --- Checking for Ollama service at %OLLAMA_API_ENDPOINT% ---
powershell -Command "echo 'Attempting to connect to Ollama via PowerShell...'; if (Test-NetConnection -ComputerName localhost -Port 11434 -WarningAction SilentlyContinue | Select-Object -ExpandProperty TcpTestSucceeded) { echo 'Ollama connection test successful.'; exit 0 } else { echo 'Ollama connection test FAILED.'; exit 1 }"
if errorlevel 1 (
    echo WARNING: Ollama service not detected at %OLLAMA_API_ENDPOINT%.
    echo Please ensure Ollama is installed and running.
    echo You can download Ollama from https://ollama.com/
    echo The agent may not function correctly without Ollama.
    echo Continuing to start the agent, but chatbot features will likely be disabled.
) else (
    echo Ollama service detected.
)
pause

REM --- 5. Git Repository Update ---
echo --- Checking for application updates ---
if not exist "%LOCAL_REPO_PATH%\.git" (
    echo Local repository not found. Cloning from %REPO_URL%...
    git clone %REPO_URL% "%LOCAL_REPO_PATH%"
    if errorlevel 1 (
        echo ERROR: Failed to clone repository. Please check your internet connection and Git installation.
        goto :error_exit
    )
    echo Repository cloned successfully.
) else (
    echo Local repository found. Fetching updates...
    cd "%LOCAL_REPO_PATH%"
    git fetch origin
    if errorlevel 1 (
        echo WARNING: Failed to fetch updates. Please check your internet connection. Will use local version.
    ) else (
        echo Fetch successful. Comparing local and remote versions...
        git rev-parse @ > ".git\local_commit.txt"
        if errorlevel 1 ( echo ERROR during git rev-parse @ & goto :error_exit )
        git rev-parse @{u} > ".gitemote_commit.txt"
        if errorlevel 1 ( echo WARNING: could not get remote commit. May happen if branch not tracking or no remote. & goto :skip_pull )

        fc ".git\local_commit.txt" ".gitemote_commit.txt" > nul
        if errorlevel 1 (
            echo Update available. Pulling changes...
            git pull origin
            if errorlevel 1 (
                echo WARNING: Failed to pull updates. You might need to resolve conflicts manually.
            ) else (
                echo Application updated successfully.
            )
        ) else (
            echo Application is up to date.
        )
        del ".git\local_commit.txt" ".gitemote_commit.txt" 2>nul
        :skip_pull
    )
    REM Ensure we are in the correct directory to run main.py, especially if LOCAL_REPO_PATH was not "."
    if /I "%cd%" neq "%~dp0%LOCAL_REPO_PATH%" (
        if "%LOCAL_REPO_PATH%" neq "." (
             echo Changing directory to %~dp0%LOCAL_REPO_PATH%
             cd /D "%~dp0%LOCAL_REPO_PATH%"
        ) else (
             REM If LOCAL_REPO_PATH is ".", change to script directory
             echo Changing directory to script directory %~dp0
             cd /D "%~dp0"
        )
    )
)
echo Update check complete.
pause

REM --- 6. Run the application ---
echo --- Starting General Purpose Agent ---
echo Running: %PYTHON_EXE% "%LOCAL_REPO_PATH%\main.py"
%PYTHON_EXE% "%LOCAL_REPO_PATH%\main.py"
echo Application finished with errorlevel %errorlevel%.
pause

goto :end

:error_exit
echo --- AN ERROR OCCURRED ---
echo Please check the messages above.
echo Errorlevel at exit: %errorlevel%
pause
:end
echo Script finished.
pause
endlocal
echo Executing endlocal.
pause
