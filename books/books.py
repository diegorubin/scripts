from os import getenv
import requests
import pymongo

ISBNDB_KEY = getenv("ISBNDB_KEY")

# Connect to MongoDB
client = pymongo.MongoClient("localhost", 27017)
db = client["books"]
collection = db["books"]


while True:
    print("input a ISBN number")
    isbn = input("> ")
    isbn = isbn.replace("\n", "")
    response = requests.get(
        f"https://api2.isbndb.com/book/{isbn}",
        headers={"Authorization": ISBNDB_KEY, "Content-Type": "application/json"},
    )

    if response.status_code == 200:
        book = response.json()
        collection.insert_one(book["book"])
        print(f"Book {book['book']['title']} added to the database")
    else:
        print("Book not found")
