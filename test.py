'''
Test Script for Base Classes
----------------------------
This script tests the interaction between the Record, Table, and Database
classes. It ensures that records can be created, inserted, retrieved,
deleted, and listed correctly.
'''

from classes import Record, Table, Database

# 1. Create a record
record1 = Record(1, {"name": "Alice", "age": 20})
record2 = Record(2, {"name": "Bob", "age": 25})

print("Created Records:")
print(record1.to_dict())
print(record2.to_dict())
print()

# 2. Create a table and insert records
table = Table("students")
table.insert(record1)
table.insert(record2)

print("Table After Insert:")
for r in table.records:
    print(r.to_dict())
print()

# 3. Delete a record
table.delete(1)

print("Table After Deleting Record 1:")
for r in table.records:
    print(r.to_dict())
print()

# 4. Add table to database
db = Database()
db.tables["students"] = table

print("Database Contents:")
print(db.to_dict())
print()

# 5. Retrieve table from database
retrieved = db.get_table("students")
print("Retrieved Table:")
print(retrieved.to_dict())

'''
Test Script for StorageManager
------------------------------
This script tests saving and loading the database using the StorageManager
class. It ensures that data is correctly written to a JSON file and restored
back into Python objects.
'''

from classes import Record, Table, Database, StorageManager

# 1. Create a database and add data
db = Database()
students = Table("students")

students.insert(Record(1, {"name": "Alice", "age": 20}))
students.insert(Record(2, {"name": "Bob", "age": 25}))

db.tables["students"] = students

print("Original Database:")
print(db.to_dict())
print()

# 2. Save the database
storage = StorageManager("test_database.json")
storage.save(db)

# 3. Load the database
loaded_db = storage.load()

print("Loaded Database:")
print(loaded_db.to_dict())
print()

# 4. Verify data matches
print("Records in loaded 'students' table:")
for record in loaded_db.get_table("students").records:
    print(record.to_dict())
