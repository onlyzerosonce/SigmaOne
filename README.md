# General Purpose Agent

A GUI-based general-purpose agent with features like checking for updates from GitHub and a chatbot interface using local language models.

## Current Features

*   **Graphical User Interface:** Built with PyQt5, providing a user-friendly way to interact with the agent.
*   **Update Functionality:**
    *   A "Check for updates" button allows the agent to check a specified GitHub repository for new versions.
    *   If updates are found, the agent can (conceptually) download them and restart.
    *   The current update repository is set to: `https://github.com/onlyzerosonce/SigmaOne`
*   **Chatbot Integration:**
    *   A chat interface (display and input field) is provided.
    *   The agent attempts to load a local language model (currently configured for `distilgpt2` from Hugging Face Transformers) to power the chatbot.
    *   If the model or its dependencies are unavailable, the agent will indicate this in the chat window.

## Setup and Installation

1.  **Prerequisites:**
    *   Python 3.7+
    *   `pip` (Python package installer)

2.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

3.  **Install required libraries using the provided scripts:**

    *   **For Windows:**
        1.  Navigate to the repository directory in Command Prompt or PowerShell.
        2.  Run the installer script:
            ```bash
            install.bat
            ```
        3.  Follow any on-screen prompts. The script will install `PyQt5`, `GitPython`, `transformers`, and `torch`.

    *   **For Linux/macOS:**
        1.  Open your terminal and navigate to the repository directory.
        2.  Make the installer script executable (if it isn't already):
            ```bash
            chmod +x install.sh
            ```
        3.  Run the installer script:
            ```bash
            ./install.sh
            ```
        4.  The script will install `PyQt5`, `GitPython`, `transformers`, and `torch` using `pip3`.

    It's still recommended to use a virtual environment before running the installer scripts if you prefer to keep dependencies isolated.
    To do so:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scriptsctivate`
    # Then run the appropriate install script.
    ```

## How to Run

Once you have installed the dependencies, you can run the agent using:

```bash
python main.py
```

## Known Issues and Limitations

*   **Network Dependency for Updates:** The "Check for updates" feature requires an active internet connection and `GitPython` to be correctly installed and configured to interact with the GitHub repository.
*   **Network Dependency for Chatbot Model:** The initial download of the chatbot language model (`distilgpt2` or other Hugging Face models) requires an active internet connection. Subsequent runs will use the cached model if available.
*   **Chatbot Model Performance:** `distilgpt2` is a relatively small model. Its conversational abilities are limited. For more advanced chatbot performance, a larger model might be necessary, which would also increase resource requirements.
*   **Update Restart Mechanism:** The application restart after an update is currently simulated by exiting the application. A more robust, platform-specific restart mechanism may be needed for production use.
*   **Testing Environment:** Some features (notably Git operations and model downloads) could not be fully tested in the development sandbox due to network restrictions.

## Future Plans

*   Enhance chatbot capabilities with more advanced models and tool usage.
*   Add more features to the agent as required.
*   Improve the update mechanism.
