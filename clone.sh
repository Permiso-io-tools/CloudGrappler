#!/bin/bash

repository_url="https://github.com/cado-security/cloudgrep"

# Clone the repository
git clone $repository_url $target_directory

# Check if the clone was successful
if [ $? -eq 0 ]; then
    echo "Repository cloned successfully."
else
    echo "Error: Failed to clone the repository."
fi
