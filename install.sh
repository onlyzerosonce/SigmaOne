#!/bin/bash

echo "Starting installation of dependencies for General Purpose Agent..."

# Function to install a package and check for errors
install_package() {
    echo "Installing $1..."
    pip3 install "$1" # Using pip3 as it's often standard for Python 3
    if [ $? -ne 0 ]; then
        echo "Failed to install $1. Please check your Python/pip setup and try again."
        exit 1
    fi
}

install_package "PyQt5"
install_package "GitPython"
install_package "transformers"
install_package "torch"

echo "All dependencies installed successfully!"
exit 0
