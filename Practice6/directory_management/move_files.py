import shutil
import os

# Change the current working directory to "first"
# This means all further operations will be performed inside the "first" folder
os.chdir("directory_management/first")

# Copy the entire folder "second" (including all its files and subfolders)
# and create a new folder called "folder"
# copytree() copies directories recursively
shutil.copytree("second", "folder")

# Go back to the parent directory (one level up)
os.chdir("..")
