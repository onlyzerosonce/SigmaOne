# General Purpose Agent

A GUI-based general-purpose agent with features like checking for updates from GitHub and a chatbot interface using a local Ollama instance.

## Current Features

*   **Graphical User Interface:** Built with PyQt5, providing a user-friendly way to interact with the agent.
*   **Automated Setup & Updates:** Start scripts (`start.bat` for Windows, `start.sh` for Linux/macOS) handle:
    *   Checking and installing required Python libraries (`PyQt5`, `GitPython`, `requests`).
    *   Checking for new versions of the agent from GitHub and automatically updating.
*   **Chatbot Integration:**
    *   Connects to a local Ollama instance for AI responses.
    *   Users need to have Ollama installed and a model (e.g., Llama2, etc.) pulled and running.
    *   The agent attempts to connect to the default Ollama API endpoint (`http://localhost:11434`).

## Prerequisites

1.  **Python 3.7+:** Download from [https://www.python.org/](https://www.python.org/) and ensure it's added to your system's PATH.
2.  **Git:** Required for the application to update itself. Download from [https://git-scm.com/](https://git-scm.com/).
3.  **Ollama:** The chatbot functionality relies on Ollama.
    *   Install Ollama from [https://ollama.com/](https://ollama.com/).
    *   Ensure Ollama is running and you have pulled a model (e.g., `ollama pull llama2`).

## How to Run

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/onlyzerosonce/SigmaOne # Or your fork's URL
    cd SigmaOne
    ```
    *(Note: The start scripts can also perform the initial clone if run in an empty directory intended for the agent, but cloning first is clearer.)*

2.  **Run the startup script:**
    *   **For Windows:**
        Navigate to the repository directory in Command Prompt or PowerShell and run:
        ```bash
        start.bat
        ```
    *   **For Linux/macOS:**
        Open your terminal, navigate to the repository directory, make the script executable (if needed, though it should be set), and run:
        ```bash
        chmod +x start.sh # If not already executable
        ./start.sh
        ```

3.  **Follow On-Screen Prompts:** The script will guide you through dependency checks, Ollama detection, updates, and then launch the agent.

## Known Issues and Limitations

*   **Ollama Dependency:** Chatbot functionality is entirely dependent on a correctly installed and running Ollama instance with a suitable model available. The agent does not install Ollama itself.
*   **Network Dependency:** Initial download of Python packages and application updates requires an active internet connection.
*   **Scripted Setup:** The startup scripts attempt to manage Python dependencies but might encounter issues on systems with complex Python environments or restrictive permissions.
*   **Update Restart Mechanism:** The application restart after an update (if implemented by `main.py` itself) is currently simulated by exiting the application. The start script handles pulling changes before launch.

## Future Plans
*   Allow user to specify Ollama model and endpoint via UI or config file.
*   Enhance error reporting and recovery in start scripts.
*   Improve the update mechanism within the application itself for a smoother experience post-update.
*   Add more features to the agent as required.
