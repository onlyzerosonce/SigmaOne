import sys
import os
import shutil # For potentially removing a repo if cloning fails midway or for cleanup
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QMessageBox

# Import git at the top, but handle ImportErrors gracefully in the methods using it.
try:
    import git
except ImportError:
    git = None # Placeholder if gitpython is not installed

# Attempt to import transformers and torch
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
except ImportError:
    AutoModelForCausalLM = None
    AutoTokenizer = None
    torch = None

class ChatApplication(QWidget):
    def __init__(self):
        super().__init__()
        self.local_repo_path = "./app_repo"
        self.tokenizer = None
        self.model = None
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
        if AutoModelForCausalLM is None or AutoTokenizer is None or torch is None:
            self.log_message("Bot: Transformers or PyTorch library not installed. Chatbot functionality disabled.")
            return

        model_name = "distilgpt2" # Using a smaller model
        self.log_message(f"Bot: Attempting to load model '{model_name}'...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.log_message(f"Bot: Model '{model_name}' loaded successfully.")
        except OSError as e: # Often indicates network issues or model not found
            self.log_message(f"Bot: Error loading model '{model_name}' (Network/OS Error): {e}. Chatbot functionality may be unavailable.")
            self.tokenizer = None
            self.model = None
        except Exception as e: # Catch any other exceptions during model loading
            self.log_message(f"Bot: Failed to load chatbot model '{model_name}': {e}. Chatbot functionality disabled.")
            self.tokenizer = None
            self.model = None

    def handle_user_input(self):
        user_text = self.user_input.text().strip()
        if not user_text:
            return

        self.log_message(f"You: {user_text}")
        self.user_input.clear()

        if self.model and self.tokenizer:
            try:
                # Encode the input text
                inputs = self.tokenizer.encode(user_text + self.tokenizer.eos_token, return_tensors='pt')

                # Generate a response
                # Ensure attention_mask is passed if the model expects it, especially for padding
                attention_mask = torch.ones(inputs.shape, dtype=torch.long, device=inputs.device)

                outputs = self.model.generate(
                    inputs,
                    attention_mask=attention_mask,
                    max_length=50,
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=2, # Prevent repetitive phrases
                    num_beams=3, # Use beam search for potentially better quality
                    early_stopping=True
                )

                # Decode the response, skipping special tokens and the input part
                response_text = self.tokenizer.decode(outputs[:, inputs.shape[-1]:][0], skip_special_tokens=True)
                self.log_message(f"Bot: {response_text}")
            except Exception as e:
                self.log_message(f"Bot: Error during response generation: {e}")
        else:
            self.log_message("Bot: Chatbot model not available.")


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
