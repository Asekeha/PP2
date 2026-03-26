from connect import conn, cur
# Import database connection and cursor from connect.py
# conn - connection to PostgreSQL
# cur - cursor to execute SQL queries


# Function to add a new contact to the database
# Takes name and phone number as input
# Uses INSERT SQL query to store data
def add_contact(name,phone):
    cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (name,phone))#used to execute a single SQL query against a database using a database connector library
    conn.commit()# Save changes to database


# Function to display all contacts
# Executes SELECT query and fetches all rows
def show():
    cur.execute("SELECT * FROM contacts")
    rows=cur.fetchall()#used to retrieve all (remaining) rows of a query result set as a list of tuples, with each tuple representing a row of data
    if not rows:
        print("No contacts found")
        return
    for i, (id, name, phone) in enumerate(rows, start=1):
        print(f"{i}. ID: {id} | Name: {name} | Phone: {phone}")

def update_phone(name, new_phone):
    cur.execute("UPDATE contacts SET phone=%s WHERE name=%s", (new_phone,name))
    conn.commit()

def update_name(old_name, new_name):
    cur.execute("UPDATE contacts SET name=%s WHERE name=%s", (new_name,old_name))
    conn.commit()

def search_name(name):
    cur.execute("SELECT * FROM contacts WHERE name ILIKE %s", (f"%{name}%",))
    rows = cur.fetchall()
    if not rows:
        print("No contacts found")
        return
    for i, (id, name, phone) in enumerate(rows, start=1):
        print(f"{i}. ID: {id} | Name: {name} | Phone: {phone}")

def search_phone(phone):
    cur.execute("SELECT * FROM contacts WHERE phone ILIKE %s", (f"%{phone}%",))
    rows = cur.fetchall()
    if not rows:
        print("No contacts found")
        return
    for i, (id, name, phone) in enumerate(rows, start=1):
        print(f"{i}. ID: {id} | Name: {name} | Phone: {phone}")

def search_phone_prefix(prefix):
    cur.execute("SELECT * FROM contacts WHERE phone LIKE %s", (f"{prefix}%",))
    rows = cur.fetchall()
    if not rows:
        print("No contacts found")
        return
    for i, (id, name, phone) in enumerate(rows, start=1):
        print(f"{i}. ID: {id} | Name: {name} | Phone: {phone}")

def delete_contact(name):
    cur.execute("DELETE FROM contacts WHERE name=%s", (name,))
    conn.commit()

# Function to import contacts from CSV file
# Reads file line by line and inserts into database
def import_csv():
    import csv

     # Open CSV file in read mode
    with open("contacts.csv", newline='', encoding='utf-8') as f:
        reader = csv.reader(f)

         # Loop through each row in CSV
        for row in reader:
            # row[0] = name, row[1] = phone
            cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (row[0], row[1]))
    conn.commit()
    print("CSV imported")

# Main program loop (menu system)
# Runs until user chooses to exit
while True:
    print("\n1)Add 2)Show 3)Update phone number 4)Update name 5)Delete 6)Import CSV 7)Search by name 8)Search by phone 9)Search by phone prefix 10)Exit")
    n=input("Choose:")

    if n=="1":
        name=input("Name: ")
        phone=input("Phone number: ")
        add_contact(name, phone)
        print("Done")
    elif n=="2":
        show()

    elif n=="3":
        name=input("Name: ")
        new_phon=input("New phone number: ")
        update_phone(name, new_phon)
        print("Done")
    elif n=="4":
        name=input("Name: ")
        new_nam=input("New name: ")
        update_name(name, new_nam)
        print("Done")
    elif n=="5":
        name=input("Name: ")
        delete_contact(name)
        print("Done")
    elif n=="6":
        import_csv()
    elif n=="7":
        name=input("Enter name to search: ")
        search_name(name)
    elif n=="8":
        phone=input("Enter phone to search: ")
        search_phone(phone)
    elif n=="9":
        prefix=input("Enter phone prefix: ")
        search_phone_prefix(prefix)
    elif n=="10":
        break
