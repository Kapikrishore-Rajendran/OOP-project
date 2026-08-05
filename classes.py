import json
from datetime import datetime

'''
Record Class
Description:
Represents a single record stored inside a table. Each record contains an ID,
a dictionary of fields, and a timestamp of when it was created.

Attributes:
- id (int): The unique identifier for the record.
- fields (dict): Stores field_name → value pairs.
- created_at (datetime): The time the record was created.

Methods:
- get(field): Returns the value of a specific field.
- set(field, value): Updates the value of a specific field.
- to_dict(): Converts the record into a dictionary for saving to JSON.
'''
class Record:
    def __init__(self, record_id, fields):
        self.id = record_id
        self.fields = fields
        self.created_at = datetime.now()

    def get(self, field):
        return self.fields.get(field)

    def set(self, field, value):
        self.fields[field] = value

    def to_dict(self):
        return {
            "id": self.id,
            "fields": self.fields,
            "created_at": self.created_at.isoformat()
        }


'''
Table Class
-----------
Description:
Represents a table inside the database. A table stores multiple Record objects
and provides operations such as insert, delete, query, and sort.

Attributes:
- name (str): The name of the table.
- records (list): A list of Record objects stored in the table.
- primary_key (str): The field used to uniquely identify each record.

Methods:
- insert(record): Adds a new record to the table.
- delete(record_id): Removes a record by its ID.
- query(query_object): Returns records that match a Query condition.
- sort(field, direction): Sorts records by a field (asc or desc).
- to_dict(): Converts the table into a dictionary for saving to JSON.
- update_record(record_id, new_fields): Updates fields of an existing record.
- record_exists(record_id): Checks if a record with given ID exists.
'''
class Table:
    def __init__(self, name, primary_key="id"):
        self.name = name
        self.records = []
        self.primary_key = primary_key

    def insert(self, record):
        for r in self.records:
            if r.id == record.id:
                raise ValueError(f"Record with ID {record.id} already exists.")
        self.records.append(record)

    def delete(self, record_id):
        for r in self.records:
            if r.id == record_id:
                self.records.remove(r)
                return True
        return False

    def query(self, query_object):
        results = []
        for record in self.records:
            if query_object.matches(record):
                results.append(record)
        return results

    def sort(self, field, direction="asc"):
        reverse = (direction == "desc")
        self.records.sort(key=lambda r: r.get(field), reverse=reverse)

    def to_dict(self):
        return {
            "name": self.name,
            "primary_key": self.primary_key,
            "records": [r.to_dict() for r in self.records]
        }

    def update_record(self, record_id, new_fields):
        for record in self.records:
            if record.id == record_id:
                record.fields.update(new_fields)
                return True
        return False

    def record_exists(self, record_id):
        return any(r.id == record_id for r in self.records)


'''
Database Class
--------------
Description:
Represents the entire database system. The database stores multiple tables
and provides methods to create, remove, and access those tables. It also
converts all data into a dictionary format for saving to JSON.

Attributes:
- tables (dict): A dictionary mapping table_name → Table object.

Methods:
- create_table(name, primary_key): Creates a new table with a given name.
- drop_table(name): Deletes a table from the database.
- get_table(name): Returns the Table object with the given name.
- to_dict(): Converts the entire database into a dictionary for saving.
'''
class Database:
    def __init__(self):
        self.tables = {}  # table_name → Table object

    def create_table(self, name, primary_key="id"):
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists.")
        from classes import Table  # avoids circular import
        self.tables[name] = Table(name, primary_key)

    def drop_table(self, name):
        if name in self.tables:
            del self.tables[name]
            return True
        return False

    def get_table(self, name):
        return self.tables.get(name)

    def to_dict(self):
        return {
            "tables": {
                name: table.to_dict()
                for name, table in self.tables.items()
            }
        }


'''
Query Class
-----------
Description:
Base class for all query types. Subclasses override the matches() and
execute() methods to perform filtering, sorting, or deletion on a table.

Attributes:
- field (str): The field being checked.
- operator (str): The comparison operator.
- value (any): The value being compared.

Methods:
- matches(record): Returns True/False (overridden in subclasses).
- execute(table): Runs the query on a table (overridden in subclasses).
'''
class Query:
    def __init__(self, field, operator, value):
        self.field = field
        self.operator = operator
        self.value = value

    def matches(self, record):
        return False

    def execute(self, table):
        return []


'''
FilterQuery Class
-----------------
Description:
Filters records in a table based on a condition. Overrides matches() and
execute() to return only the records that meet the filter condition.

Methods:
- matches(record): Checks if the record meets the condition.
- execute(table): Returns a list of matching records.
'''
class FilterQuery(Query):
    def matches(self, record):
        record_value = record.get(self.field)

        if self.operator == "=":
            return record_value == self.value
        elif self.operator == ">":
            return record_value > self.value
        elif self.operator == "<":
            return record_value < self.value
        elif self.operator == "!=":
            return record_value != self.value
        return False

    def execute(self, table):
        return [record for record in table.records if self.matches(record)]


'''
SortQuery Class
---------------
Description:
Sorts records in a table based on a field and direction. Overrides execute()
to return a sorted list of records.

Methods:
- compare(record1, record2): Compares two records.
- execute(table): Returns sorted records.
'''
class SortQuery(Query):
    def __init__(self, field, direction="asc"):
        super().__init__(field, None, None)
        self.direction = direction

    def compare(self, record1, record2):
        v1 = record1.get(self.field)
        v2 = record2.get(self.field)
        if self.direction == "asc":
            return (v1 > v2) - (v1 < v2)
        return (v2 > v1) - (v2 < v1)

    def execute(self, table):
        return sorted(
            table.records,
            key=lambda r: r.get(self.field),
            reverse=(self.direction == "desc")
        )


'''
DeleteQuery Class
-----------------
Description:
Deletes records from a table that match a condition. Overrides matches() and
execute() to remove records and return how many were deleted.

Methods:
- matches(record): Checks if the record should be deleted.
- execute(table): Deletes matching records and returns count.
'''
class DeleteQuery(Query):
    def matches(self, record):
        record_value = record.get(self.field)

        if self.operator == "=":
            return record_value == self.value
        elif self.operator == "!=":
            return record_value != self.value
        return False

    def execute(self, table):
        to_delete = [r for r in table.records if self.matches(r)]
        for r in to_delete:
            table.records.remove(r)
        return len(to_delete)


'''
StorageManager Class
--------------------
Description:
Handles saving and loading the entire database to and from a JSON file.
This class converts Python objects (Database, Table, Record) into JSON-
friendly dictionaries and restores them back into objects when loading.
It also includes basic error handling for missing files or invalid data.

Attributes:
- filename (str): The name of the JSON file used for storage.

Methods:
- save(database): Saves the database object to a JSON file.
- load(): Loads the database from the JSON file and returns a Database object.
- _dict_to_database(data): Internal helper that rebuilds Database objects.
- backup(): Creates a backup copy of the JSON file.
'''
class StorageManager:
    def __init__(self, filename="database.json"):
        self.filename = filename

    def save(self, database):
        try:
            with open(self.filename, "w") as f:
                json.dump(database.to_dict(), f, indent=4)
            print("Database saved successfully.")
        except Exception as e:
            print(f"Error saving database: {e}")

    def load(self):
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                print("Database loaded successfully.")
                return self._dict_to_database(data)
        except FileNotFoundError:
            print("No existing database found. Creating a new one.")
            return Database()
        except Exception as e:
            print(f"Error loading database: {e}")
            return Database()

    def _dict_to_database(self, data):
        db = Database()

        for table_name, table_data in data["tables"].items():
            table = Table(table_name, table_data["primary_key"])

            for record_data in table_data["records"]:
                record = Record(
                    record_data["id"],
                    record_data["fields"]
                )
                record.created_at = datetime.fromisoformat(record_data["created_at"])
                table.insert(record)

            db.tables[table_name] = table

        return db

    def backup(self):
        import os, shutil
        try:
            os.makedirs("backup", exist_ok=True)
            shutil.copy(self.filename, "backup/database_backup.json")
            print("Backup created successfully.")
        except Exception as e:
            print(f"Error creating backup: {e}")
