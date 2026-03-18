# Open the file "example.txt" in exclusive creation mode ("x")
# This mode creates a new file, but raises an error if the file already exists
with open("example.txt", "x") as f:
    # Write text into the file
    # "\n" is a newline character, so "Python is fun" will be written on a new line
    f.write("Hello \nPython is fun")

# Open the file again in read mode ("r")
with open("example.txt", "r") as f:
    # Read the entire content of the file
    content = f.read()
    
    # Print the content to the console
    print(content)
