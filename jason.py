from pymongo import MongoClient

# Mongo URI
MONGO_URI = "mongodb+srv://thesevasetufoundation:QDBxMA83Wsiamvyb@sevasetu.qplys.mongodb.net/Khack?retryWrites=true&w=majority&tls=true"

# Connect to MongoDB
client = MongoClient(MONGO_URI)

# Access the specific database
db = client['Khack']

# Access a specific collection, for example, 'donations'
collection = db['users']  # Replace with your actual collection name

# Query the first 5 documents in the collection
documents = collection.find().limit(5)

# Print the documents
for document in documents:
    print(document)

# Close the connection
client.close()
