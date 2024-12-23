from pymongo import MongoClient

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/Khack"
client = MongoClient(MONGO_URI)

# Specify the database and collection
db = client["Khack"]
collection = db["users"]  # Replace 'users' with your collection name

# Update all documents to add the 'friends' field if it doesn't exist
result = collection.update_many(
    {"requests": {"$exists": False}},  # Only update documents without 'friends' field
    {"$set": {"requests": []}}        # Add an empty 'friends' array
)

print(f"Matched documents: {result.matched_count}")
print(f"Modified documents: {result.modified_count}")
