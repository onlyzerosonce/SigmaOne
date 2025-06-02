import sys
import os
import shutil # For potentially removing a repo if cloning fails midway or for cleanup
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QMessageBox

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
        self.local_repo_path = "./app_repo"
        self.ollama_available = False
        self.ollama_model_name = "llama2" # Default model
        self.initUI()
        self.load_chatbot_model() # Attempt to load the model after UI is initialized

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

    def check_for_updates(self):
        self.log_message("Checking for updates...")

        if git is None:
            self.log_message("Error: GitPython library is not installed. Update functionality disabled.")
            QMessageBox.critical(self, "Update Error", "GitPython library is not installed. Please install it to use the update feature.")
            return

        repo_url = "https://github.com/onlyzerosonce/SigmaOne"

        # The following check is no longer needed as the URL is now hardcoded.
        # if repo_url == "YOUR_GITHUB_REPO_URL_HERE":
        #     self.log_message("Error: Repository URL is not configured.")
        #     QMessageBox.warning(self, "Update Error", "The repository URL for updates is not configured.")
        #     return

        try:
            repo = None
            if os.path.exists(self.local_repo_path):
                self.log_message(f"Local repository found at {self.local_repo_path}. Opening...")
                try:
                    repo = git.Repo(self.local_repo_path)
                except git.InvalidGitRepositoryError:
                    self.log_message(f"Invalid Git repository at {self.local_repo_path}. Removing and re-cloning.")
                    if os.path.isdir(self.local_repo_path): # Check if it's a dir before rmtree
                        shutil.rmtree(self.local_repo_path)
                    repo = None

            if repo is None:
                self.log_message(f"Cloning repository from {repo_url} into {self.local_repo_path}...")
                try:
                    repo = git.Repo.clone_from(repo_url, self.local_repo_path)
                    self.log_message("Repository cloned successfully.")
                except git.GitCommandError as e:
                    self.log_message(f"Git clone error: {e}")
                    QMessageBox.critical(self, "Update Error", f"Failed to clone repository: {e}")
                    return

            self.log_message("Fetching latest changes from remote (origin)...")
            try:
                origin = repo.remotes.origin
                origin.fetch()
            except git.GitCommandError as e:
                self.log_message(f"Git fetch error: {e}")
                QMessageBox.critical(self, "Update Error", f"Failed to fetch updates: {e}")
                return

            local_commit = repo.head.commit
            remote_commit_ref = None
            try:
                remote_commit_ref = repo.remotes.origin.refs['main']
            except IndexError:
                try:
                    remote_commit_ref = repo.remotes.origin.refs['master']
                except IndexError:
                    self.log_message("Error: Could not find 'main' or 'master' branch on remote.")
                    QMessageBox.critical(self, "Update Error", "Could not determine the default branch (main/master) on the remote repository.")
                    return

            remote_commit = remote_commit_ref.commit

            self.log_message(f"Local commit: {local_commit.hexsha}")
            self.log_message(f"Remote commit: {remote_commit.hexsha}")

            if local_commit != remote_commit:
                self.log_message("Update available. Pulling changes...")
                try:
                    origin.pull()
                    self.log_message("Update downloaded successfully.")
                    QMessageBox.information(self, "Update Complete", "Application updated. Please restart the application.")
                    self.log_message("Simulating application restart by quitting...")
                    QApplication.instance().quit()
                except git.GitCommandError as e:
                    self.log_message(f"Git pull error: {e}")
                    QMessageBox.critical(self, "Update Error", f"Failed to pull updates: {e}")
            else:
                self.log_message("Application is up to date.")
                QMessageBox.information(self, "No Updates", "Your application is currently up to date.")

        except git.GitCommandError as e:
            self.log_message(f"A Git command failed: {e}")
            QMessageBox.critical(self, "Update Error", f"An error occurred during Git operation: {e}")
        except Exception as e:
            self.log_message(f"An unexpected error occurred during update: {e}")
            QMessageBox.critical(self, "Update Error", f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChatApplication()
    ex.show()
    sys.exit(app.exec_())
