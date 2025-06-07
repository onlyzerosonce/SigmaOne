# SigmaOne: General Purpose Agent

SigmaOne is a cross-platform desktop application that acts as a general-purpose AI agent with a chat interface. It is built using Python and PyQt5, and integrates with Ollama for local LLM (Large Language Model) inference. The app can also check for updates from its GitHub repository.

## Features
- **Chat Interface:** Simple, user-friendly chat window for interacting with the agent.
- **Ollama Integration:** Connects to a local Ollama server for LLM-based responses.
- **Update Checker:** Checks for updates from the official GitHub repository.
- **Cross-Platform:** Works on Linux, Windows, and macOS (with appropriate Python and dependencies).

## Requirements
- Python 3.7+
- [Ollama](https://ollama.com/) running locally (for LLM features)
- The following Python packages:
  - PyQt5
  - GitPython
  - requests

## Installation

### Linux/macOS
1. **Clone the repository:**
   ```bash
   git clone https://github.com/onlyzerosonce/SigmaOne.git
   cd SigmaOne
   ```
2. **Run the install script:**
   ```bash
   bash install.sh
   ```
   Or manually install dependencies:
   ```bash
   pip3 install -U PyQt5 GitPython requests
   ```
3. **(Optional) Start Ollama:**
   - Download and run Ollama from [https://ollama.com/](https://ollama.com/)
   - Make sure it is running at `http://localhost:11434`

4. **Start the application:**
   ```bash
   bash start.sh
   ```
   Or:
   ```bash
   python3 main.py
   ```

### Windows
1. Double-click `install.bat` to install dependencies.
2. Double-click `start.bat` to run the application.

## Building a Standalone Executable
To build a standalone executable (using PyInstaller):
```bash
python3 build.py
```
The output will be in the `dist/` directory.

## Usage
- Type your message in the input box and press Enter.
- The agent will respond using the connected Ollama model.
- Use the "Check for updates" button to see if a new version is available.

## Troubleshooting
- **Ollama not detected:** Ensure Ollama is running locally at `http://localhost:11434`.
- **Missing dependencies:** Run the install script or manually install required Python packages.
- **Update issues:** Make sure the app is running inside a valid Git repository clone.

## License
See [LICENSE](https://github.com/onlyzerosonce/SigmaOne/blob/main/LICENSE) for details.

## Credits
- [Ollama](https://ollama.com/)
- [PyQt5](https://riverbankcomputing.com/software/pyqt/)
- [GitPython](https://gitpython.readthedocs.io/en/stable/)
