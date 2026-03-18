import shutil
import os

# Copy the file "example.txt" and create a new file called "copy.txt"
# shutil.copy() duplicates the file along with its content
shutil.copy("example.txt", "copy.txt")

# Delete the file "copy.txt"
# os.remove() removes (deletes) the specified file from the system
os.remove("copy.txt")

# Delete the original file "example.txt"
os.remove("example.txt")
