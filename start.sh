#!/bin/bash

# --- Configuration ---
PYTHON_CMD="python3"
PIP_CMD="pip3"
REPO_URL="https://github.com/onlyzerosonce/SigmaOne"
LOCAL_REPO_PATH="." # Assuming script is run from the repo root
OLLAMA_API_ENDPOINT="http://localhost:11434"
REQUIRED_PACKAGES="PyQt5 GitPython requests"

# --- Helper function to check if a command exists ---
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- 1. Check for Python ---
echo "Checking for Python 3..."
if ! command_exists $PYTHON_CMD; then
    echo "Python 3 is not found. Please install Python 3."
    # Attempt to guide based on common package managers
    if command_exists apt-get; then
        echo "You might be able to install it with: sudo apt-get update && sudo apt-get install python3 python3-pip"
    elif command_exists yum; then
        echo "You might be able to install it with: sudo yum install python3 python3-pip"
    elif command_exists brew; then
        echo "You might be able to install it with: brew install python3"
    else
        echo "Please visit https://www.python.org/downloads/"
    fi
    exit 1
fi
echo "Python 3 found."

# --- 2. Check for Pip ---
echo "Checking for Pip 3..."
if ! command_exists $PIP_CMD; then
    echo "Pip 3 is not found."
    echo "Attempting to install pip for Python 3..."
    if command_exists apt-get; then
        sudo apt-get update && sudo apt-get install python3-pip -y
    elif command_exists yum; then
        sudo yum install python3-pip -y
    else
        echo "Please ensure pip is installed for Python 3 (e.g., often installed with python3 or via 'python3 -m ensurepip --upgrade')."
    fi
    if ! command_exists $PIP_CMD; then
        echo "Failed to install Pip 3. Please install it manually."
        exit 1
    fi
fi
echo "Pip 3 found."

# --- 3. Install/Upgrade Python dependencies ---
echo "Checking and installing Python packages: $REQUIRED_PACKAGES..."
for package in $REQUIRED_PACKAGES; do
    echo "Installing/updating $package..."
    if ! $PIP_CMD install --upgrade "$package"; then
        echo "Failed to install $package. Please check your Python/pip setup and internet connection."
        exit 1
    fi
done
echo "All required Python packages are installed/updated."

# --- 4. Check for Ollama ---
echo "Checking for Ollama service at $OLLAMA_API_ENDPOINT..."
# Using curl to check. -s for silent, -f for fail fast (non-2xx is an error), -o /dev/null to discard output.
if curl -s -f -o /dev/null "$OLLAMA_API_ENDPOINT/api/tags"; then # Check a valid Ollama endpoint
    echo "Ollama service detected."
else
    echo "Ollama service not detected or not responding at $OLLAMA_API_ENDPOINT."
    echo "Please ensure Ollama is installed and running."
    echo "You can download Ollama from https://ollama.com/"
    echo "The agent may not function correctly without Ollama."
    echo "Continuing to start the agent, but chatbot features will likely be disabled."
    echo ""
fi

# --- 5. Git Repository Update ---
echo "Checking for application updates..."
if [ ! -d "$LOCAL_REPO_PATH/.git" ]; then
    echo "Local repository not found. Cloning from $REPO_URL..."
    if ! git clone "$REPO_URL" "$LOCAL_REPO_PATH"; then
        echo "Failed to clone repository. Please check your internet connection and Git installation."
        exit 1
    fi
    echo "Repository cloned successfully."
    cd "$LOCAL_REPO_PATH" || exit 1 # Enter the repo dir
else
    echo "Local repository found. Fetching updates..."
    cd "$LOCAL_REPO_PATH" || exit 1 # Enter the repo dir
    if ! git fetch origin; then
        echo "Failed to fetch updates. Please check your internet connection. Continuing with local version."
    else
        LOCAL_COMMIT=$(git rev-parse @)
        REMOTE_COMMIT=$(git rev-parse @{u}) # Fails if branch not tracking remote, or no remote

        if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
            echo "Update available. Pulling changes..."
            if ! git pull origin; then
                echo "Failed to pull updates. You might need to resolve conflicts manually."
            else
                echo "Application updated successfully."
            fi
        else
            echo "Application is up to date."
        fi
    fi
fi

# --- 6. Run the application ---
echo "Starting General Purpose Agent..."
$PYTHON_CMD main.py

echo "Application finished."
# No pause needed for .sh typically, window stays open.
exit 0
