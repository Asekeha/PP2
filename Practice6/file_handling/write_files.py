# Open the file "example.txt" in append mode ("a")
# This means new data will be added to the end of the file without overwriting existing content
with open("example.txt", "a") as f:
    # Write a string to the file
    # "\n" represents a newline character, so the text starts on a new line
    f.write("\nI like KBTU")

# Open the same file in read mode ("r")
with open("example.txt", "r") as f:
    # Read the entire content of the file using read()
    content = f.read()
    
    # Print the file content to the console
    print(content)
