import sys
import os
import shutil # For potentially removing a repo if cloning fails midway or for cleanup
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QMessageBox, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon # For loading an icon from a file

# Import git at the top, but handle ImportErrors gracefully in the methods using it.
try:
    import git
except ImportError:
    git = None # Placeholder if gitpython is not installed

# Attempt to import requests and json for Ollama integration
try:
    import requests
    import json
except ImportError:
    requests = None
    json = None

class ChatApplication(QWidget):
    def __init__(self):
        super().__init__()
        self.local_repo_path = "./app_repo" # Path for git operations
        self.ollama_available = False
        self.ollama_model_name = "llama2" # Default Ollama model
        self.app_icon_path = "icon.png" # Path to the application icon

        self.initUI() # Standard UI setup
        self.initTrayIcon() # Setup for the system tray icon

        self.load_chatbot_model() # Load chatbot model (Ollama check)

        # Flag to determine if quit is from tray or window close event
        self._is_quitting_via_tray = False

    def initTrayIcon(self):
        self.tray_icon = QSystemTrayIcon(self)

        icon = QIcon(self.app_icon_path)
        if icon.isNull():
            self.log_message(f"System Tray: Icon not found at '{self.app_icon_path}', using default.")
        self.tray_icon.setIcon(icon)

        tray_menu = QMenu()

        show_hide_action = QAction("Show/Hide Window", self)
        show_hide_action.triggered.connect(self.show_hide_window)
        tray_menu.addAction(show_hide_action)

        check_updates_action = QAction("Check for Updates (Tray)", self)
        check_updates_action.triggered.connect(self.tray_check_for_updates)
        tray_menu.addAction(check_updates_action)

        tray_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.tray_quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.handle_tray_activation)

    def handle_tray_activation(self, reason):
        # Show/hide window on left click (QSystemTrayIcon.Trigger)
        if reason == QSystemTrayIcon.Trigger:
            self.show_hide_window()

    def show_hide_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.showNormal()
            self.activateWindow() # Bring to front

    def tray_check_for_updates(self):
        # This method now calls the refactored check_for_updates.
        self.log_message("System Tray: Initiating update check.")
        self.check_for_updates(from_tray=True)

    def tray_quit_application(self):
        self.log_message("System Tray: Quit action triggered.")
        self._is_quitting_via_tray = True
        self.tray_icon.hide() # Hide tray icon immediately
        QApplication.instance().quit() # Quit the application

    # Override closeEvent to hide to tray instead of quitting
    def closeEvent(self, event):
        if self._is_quitting_via_tray:
            self.log_message("Application: Quitting via tray action.")
            event.accept() # Allow quit
        else:
            self.log_message("Application: Close event intercepted, hiding to tray.")
            event.ignore() # Intercept close event
            self.hide()    # Hide window to tray
            if self.tray_icon.isVisible(): # Show message only if tray icon is actually visible
                self.tray_icon.showMessage(
                    "General Purpose Agent",
                    "Application minimized to system tray.",
                    QSystemTrayIcon.Information,
                    2000 # Duration in ms
                )

    def initUI(self):
        self.setWindowTitle("General Purpose Agent")
        self.setGeometry(100, 100, 400, 500)  # x, y, width, height

        layout = QVBoxLayout()

        # Update Button
        self.update_button = QPushButton("Check for updates")
        self.update_button.clicked.connect(self.check_for_updates)
        layout.addWidget(self.update_button)

        # Chat Display Area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # User Input Field
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your message here...")
        self.user_input.returnPressed.connect(self.handle_user_input) # Connect here
        layout.addWidget(self.user_input)

        self.setLayout(layout)

    def log_message(self, message):
        self.chat_display.append(message)
        QApplication.processEvents() # Ensure UI updates

    def load_chatbot_model(self):
        if requests is None or json is None:
            self.log_message("Bot: 'requests' or 'json' library not installed. Ollama functionality disabled.")
            self.ollama_available = False
            return

        self.log_message("Bot: Checking Ollama connection and model availability...")
        try:
            response = requests.get("http://localhost:11434/api/tags")
            response.raise_for_status() # Raise an exception for HTTP errors
            models_data = response.json()

            available_models = [model_info["name"] for model_info in models_data.get("models", [])]

            # Check if self.ollama_model_name (or a version of it like self.ollama_model_name:latest) is available
            model_found = any(self.ollama_model_name in model_name for model_name in available_models)

            if model_found:
                self.ollama_available = True
                self.log_message(f"Bot: Ollama connected. Model '{self.ollama_model_name}' is available.")
            else:
                self.ollama_available = False
                self.log_message(f"Bot: Ollama connected, but model '{self.ollama_model_name}' not found. Available models: {', '.join(available_models) if available_models else 'None'}.")
        except requests.exceptions.ConnectionError:
            self.log_message("Bot: Ollama service not found. Please ensure Ollama is running at http://localhost:11434.")
            self.ollama_available = False
        except requests.exceptions.RequestException as e:
            self.log_message(f"Bot: Error connecting to Ollama or listing models: {e}")
            self.ollama_available = False
        except json.JSONDecodeError:
            self.log_message("Bot: Error decoding response from Ollama /api/tags. Is it running correctly?")
            self.ollama_available = False
        except Exception as e: # Catch any other unexpected errors
            self.log_message(f"Bot: An unexpected error occurred while checking Ollama: {e}")
            self.ollama_available = False

    def handle_user_input(self):
        user_text = self.user_input.text().strip()
        if not user_text:
            return

        self.log_message(f"You: {user_text}")
        self.user_input.clear()

        if not self.ollama_available:
            self.log_message("Bot: Ollama is not available. Cannot process message.")
            return

        if requests is None or json is None:
            self.log_message("Bot: 'requests' or 'json' library not installed for Ollama. Cannot process message.")
            return

        payload = {
            "model": self.ollama_model_name,
            "prompt": user_text,
            "stream": False
        }
        self.log_message("Bot: Sending message to Ollama...")
        try:
            response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60) # Added timeout
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            # Process potentially newline-delimited JSON responses from Ollama
            final_response_json = None
            for line in response.iter_lines():
                if line: # filter out keep-alive new lines
                    try:
                        json_line = json.loads(line)
                        final_response_json = json_line # Keep overwriting to get the last complete JSON object
                    except json.JSONDecodeError:
                        self.log_message(f"Bot: Warning - Could not decode a line from Ollama stream: {line}")
                        continue # Skip malformed lines

            if final_response_json and "response" in final_response_json:
                bot_response = final_response_json["response"]
                self.log_message(f"Bot: {bot_response.strip()}")
            elif final_response_json and "error" in final_response_json:
                self.log_message(f"Bot: Ollama error: {final_response_json['error']}")
            elif not final_response_json:
                 self.log_message("Bot: No valid JSON response received from Ollama.")
            else:
                self.log_message("Bot: Received an unexpected response format from Ollama.")

        except requests.exceptions.Timeout:
            self.log_message("Bot: Request to Ollama timed out. The model might be taking too long to respond.")
        except requests.exceptions.ConnectionError:
            self.log_message("Bot: Connection error while sending message to Ollama. Is it still running?")
            self.ollama_available = False # Potentially set to false if connection fails
        except requests.exceptions.HTTPError as e:
             self.log_message(f"Bot: HTTP error from Ollama API - Status {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            self.log_message(f"Bot: Error sending request to Ollama: {e}")
        except json.JSONDecodeError: # Should be caught by line-by-line decoding, but as a fallback
            self.log_message("Bot: Error decoding the final Ollama response.")
        except Exception as e:
            self.log_message(f"Bot: Error processing Ollama response: {e}")

    def check_for_updates(self, from_tray=False):
        source_msg = "from tray" if from_tray else "from UI button"
        self.log_message(f"Checking for updates ({source_msg})...")

        if git is None:
            self.log_message("Error: GitPython library is not installed. Update functionality disabled.")
            QMessageBox.critical(self, "Update Error", "GitPython library is not installed. Please install it to use the update feature.")
            return

        repo_url = "https://github.com/onlyzerosonce/SigmaOne"

        path_to_check_git = self.local_repo_path # Default path, e.g., "./app_repo"
        # If self.local_repo_path does not exist or doesn't contain .git, try current directory "."
        if not os.path.exists(os.path.join(path_to_check_git, ".git")):
            self.log_message(f"'.git' not found in '{os.path.abspath(path_to_check_git)}'. Trying current directory '.'")
            path_to_check_git = "."

        try:
            if not os.path.exists(os.path.join(path_to_check_git, ".git")):
                self.log_message(f"Cannot check for updates: '.git' folder not found in '{os.path.abspath(self.local_repo_path)}' or in current directory '{os.path.abspath('.')}'.")
                QMessageBox.information(self, "Update Check", f"Cannot check for updates (not a Git repository).\nPlease visit {repo_url} for the latest version.")
                return

            self.log_message(f"Using Git repository at '{os.path.abspath(path_to_check_git)}'")
            repo = git.Repo(path_to_check_git)

            # Handle detached HEAD state (e.g., after a direct checkout of a commit)
            if repo.head.is_detached:
                self.log_message("Warning: Git HEAD is detached. Cannot reliably check for updates against a branch.")
                QMessageBox.warning(self, "Update Check", "Your local repository is in a 'detached HEAD' state. Cannot automatically check for updates. Please manually check the repository for new versions.")
                return

            self.log_message("Fetching latest changes from remote (origin)...")
            origin = repo.remotes.origin
            origin.fetch()

            local_commit = repo.head.commit

            # Determine remote reference (main or master)
            remote_ref_name = None
            if 'main' in repo.remotes.origin.refs:
                remote_ref_name = 'main'
            elif 'master' in repo.remotes.origin.refs:
                remote_ref_name = 'master'
            else:
                self.log_message("Error: Could not find 'main' or 'master' branch on remote 'origin'.")
                QMessageBox.critical(self, "Update Error", "Could not determine the default branch (main/master) on the remote repository.")
                return

            remote_commit = repo.remotes.origin.refs[remote_ref_name].commit

            self.log_message(f"Local commit: {local_commit.hexsha} ({repo.active_branch.name})")
            self.log_message(f"Remote commit: {remote_commit.hexsha} (origin/{remote_ref_name})")

            if local_commit != remote_commit:
                self.log_message("Update available.")
                QMessageBox.information(self, "Update Available",
                                        f"A new version is available on branch '{remote_ref_name}' at {repo_url}\n"
                                        "Please consider updating your local repository or downloading the latest version.")
            else:
                self.log_message("Application is up to date.")
                QMessageBox.information(self, "No Updates", f"Your application (branch '{repo.active_branch.name}') is currently up to date with 'origin/{remote_ref_name}'.")

        except git.InvalidGitRepositoryError:
            self.log_message(f"Error: The path '{os.path.abspath(path_to_check_git)}' is not a valid Git repository.")
            QMessageBox.warning(self, "Update Error", f"The application could not find a valid Git repository at the expected location: {os.path.abspath(path_to_check_git)}")
        except git.NoSuchPathError:
             self.log_message(f"Error: The path '{os.path.abspath(path_to_check_git)}' does not exist for Git operations.")
             QMessageBox.warning(self, "Update Error", f"The application path for Git operations does not exist: {os.path.abspath(path_to_check_git)}")
        except git.GitCommandError as e:
            self.log_message(f"A Git command failed: {e}")
            QMessageBox.critical(self, "Update Error", f"An error occurred during Git operation: {e}")
        except Exception as e:
            self.log_message(f"An unexpected error occurred during update check: {e}")
            QMessageBox.critical(self, "Update Error", f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChatApplication()
    ex.show()
    sys.exit(app.exec_())
