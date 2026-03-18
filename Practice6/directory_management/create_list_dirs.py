import os
from pathlib import Path

# All folders will be created inside "directory_management"
# Define base directory where everything will be created
base_path = "directory_management"

# Create a nested directory structure: first/second/third/fourth
# makedirs() creates all intermediate directories if they do not exist
os.makedirs(f"{base_path}/first/second/third/fourth")

# Change the current working directory to "first"

os.chdir(f"{base_path}/first")

# List of folder names to be created inside "first"
folders = ["data", "images", "text"]

# Loop through the list and create each directory
for i in folders:
        # mkdir() creates a single directory
    os.mkdir(i)
# Print the list of files and directories inside the current folder ("first")
print(os.listdir())

# Go back to the parent directory (one level up)
os.chdir("..")
   # Iterate through all files and directories in the current path
for file in Path().iterdir():
        # Check if the file has ".py" extension
    if file.suffix == ".py":
        print(file)
