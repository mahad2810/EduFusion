from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")  # Adjust the URI if needed
db = client['Khack']
users_collection = db['users']

# Update social_media_links field to be a dictionary with github and linkedin
for user in users_collection.find():
    # Check if social_media_links exists and is a list
    if 'social_media_links' in user and isinstance(user['social_media_links'], list):
        social_media_links = user['social_media_links']
        
        # Ensure there are at least two items in the list for github and linkedin
        updated_social_media_links = {
            'github': social_media_links[0] if len(social_media_links) > 0 else '',
            'linkedin': social_media_links[1] if len(social_media_links) > 1 else ''
        }
        
        # Update the user document with the new social_media_links structure
        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'social_media_links': updated_social_media_links}}
        )

print("social_media_links updated to dictionary format with github and linkedin.")
