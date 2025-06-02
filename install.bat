@echo off
echo Starting installation of dependencies for General Purpose Agent...

echo Installing PyQt5...
pip install PyQt5
if errorlevel 1 (
    echo Failed to install PyQt5. Please check your Python/pip setup and try again.
    goto :error
)

echo Installing GitPython...
pip install GitPython
if errorlevel 1 (
    echo Failed to install GitPython. Please check your Python/pip setup and try again.
    goto :error
)

echo Installing transformers...
pip install transformers
if errorlevel 1 (
    echo Failed to install transformers. Please check your Python/pip setup and try again.
    goto :error
)

echo Installing torch...
pip install torch
if errorlevel 1 (
    echo Failed to install torch. Please check your Python/pip setup and try again.
    goto :error
)

echo All dependencies installed successfully!
goto :end

:error
echo An error occurred during installation.
:end
pause
