import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask, session, redirect, url_for, jsonify
from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_pymongo import PyMongo
from oauthlib.oauth2 import WebApplicationClient
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from PIL import Image
import smtplib
import random
from werkzeug.security import generate_password_hash
from bson import ObjectId
from bson.objectid import ObjectId

app = Flask(__name__)
# MongoDB configuration
app.config["MONGO_URI"] = "mongodb+srv://thesevasetufoundation:QDBxMA83Wsiamvyb@sevasetu.qplys.mongodb.net/Khack?retryWrites=true&w=majority&tls=true"
app.secret_key = "supersecretkey"
mongo = PyMongo(app)

# Google OAuth configuration
GOOGLE_CLIENT_ID = "1043891935318-5d2njou75j44rtbi9bm0e2tm1nupq0pq.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "thesevasetufoundation@gmail.com"
EMAIL_PASSWORD = "rnri bops ohnz hbbu"  # Use environment variables for better security

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/")
def landing_page():
    return render_template("land.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = mongo.db.users.find_one({"email": email, "password": password})
        if user:
            session["user_email"] = email
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


import re

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    # Strong password validation
    if not validate_password(password):
        flash(
            "Password must be at least 8 characters long, include an uppercase letter, "
            "a lowercase letter, a number, and a special character.", 
            "danger"
        )
        return redirect(url_for("login"))

    # Check if the email is already registered
    if mongo.db.users.find_one({"email": email}):
        flash("Email already registered. Please log in.", "danger")
        return redirect(url_for("login"))

    # Create a user document
    user = {
        "name": name,
    "email": email,
    "password": None,
    "phone_number": "",
    "college": "",
    "state": "",
    "city": "",
    "social_media_links": [],
    "skills": {},  # Dictionary with skill name as key and status as value
    "projects": []  # Array of dictionaries with structure { "project_name": ..., "project_lead_name": ..., "description": ..., "city": ..., "skills": ..., "status": ... }
    }

    # Insert user into MongoDB
    mongo.db.users.insert_one(user)
    session["user_email"] = email
    return redirect(url_for("home"))


def validate_password(password):
    """
    Validates if the password is strong based on the following criteria:
    - At least 8 characters.
    - Contains at least one uppercase letter.
    - Contains at least one lowercase letter.
    - Contains at least one number.
    - Contains at least one special character.
    - Does not contain spaces.
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):  # Uppercase
        return False
    if not re.search(r"[a-z]", password):  # Lowercase
        return False
    if not re.search(r"[0-9]", password):  # Digit
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # Special character
        return False
    if re.search(r"\s", password):  # No spaces
        return False
    return True


@app.route("/login/google")
def google_login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri="http://localhost:5000/login/google/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/google/callback")
def google_callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url="http://localhost:5000/login/google/callback",
        code=code,
    )
    token_response = requests.post(
        token_url, headers=headers, data=body, auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    )
    client.parse_request_body_response(token_response.text)

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    user_info = userinfo_response.json()
    email = user_info["email"]
    name = user_info.get("name", "User")

    user = mongo.db.users.find_one({"email": email})
    if not user:
       mongo.db.users.insert_one({
    "name": name,
    "email": email,
    "password": None,
    "phone_number": "",
    "college": "",
    "state": "",
    "city": "",
    "social_media_links": [],
    "skills": {},  # Dictionary with skill name as key and status as value
    "projects": []  # Array of dictionaries with structure { "project_name": ..., "project_lead_name": ..., "description": ..., "city": ..., "skills": ..., "status": ... }
})


    session["user_email"] = email
    return redirect(url_for("home"))

def send_email_with_otp(email, otp):
    subject = "Your OTP for Password Reset"
    body = f"Your OTP for resetting the password is: {otp}"
    message = MIMEMultipart()
    message["From"] = "thesevasetufoundation@gmail.com"
    message["To"] = email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("thesevasetufoundation@gmail.com", "rnri bops ohnz hbbu")  # Use your app password
        server.sendmail(message["From"], message["To"], message.as_string())
        server.quit()
        print(f"OTP sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

def generate_otp(length=6):
    """
    Generate a numeric OTP of the specified length.
    Default length is 6.
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Generate OTP and send email
        session["otp"] = generate_otp()
        send_email_with_otp(email, session["otp"])
        return jsonify({"message": "OTP sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    print("Received data:", data)  # Debug: Log the incoming data
    print(f"Session data: {session}")  # Debug: Log the session data

    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400

    otp = data.get("otp")
    session["email"] = data.get("email")

    if not otp:
        return jsonify({"error": "OTP is required"}), 400

    # Compare OTP as strings
    if "otp" in session and otp == session["otp"]:
        return jsonify({"message": "OTP verified successfully"})

    return jsonify({"error": "Invalid OTP"}), 400


@app.route('/api/reset-password', methods=['POST'])  # Ensure route matches frontend
def reset_password():
    try:
        data = request.get_json()
        new_password = data.get("newPassword")

        if not new_password:
            return jsonify({"success": False, "message": "New password is required"}), 400

        email = session.get("email")
        if not email:
            return jsonify({"success": False, "message": "Session expired. Please log in again."}), 401

        # Hash the new password for security
        hashed_password = generate_password_hash(new_password)

        # Update password in the database
        result = mongo.db.users.update_one(
            {"email": email},  # Find the user by email
            {"$set": {"password": hashed_password}}  # Update the password field
        )

        if result.modified_count == 1:
            session.pop("otp", None)
            session.pop("email", None)
            return jsonify({"success": True, "message": "Password reset successful"})
        else:
            return jsonify({"success": False, "message": "Failed to update password in the database."}), 500

    except Exception as e:
        print(f"Error resetting password: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500


    
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/dashboard")
def dashboard():
    user_email = session.get("user_email")
    if not user_email:
        return redirect(url_for("login"))  # Redirect to login if not logged in

    # Fetch user details from MongoDB, including social_media_links
    user = mongo.db.users.find_one({"email": user_email}, {"_id": 0})

    # Organize skills by status
    skills_ongoing = [skill for skill, status in user.get("skills", {}).items() if status == "ongoing"]
    skills_completed = [skill for skill, status in user.get("skills", {}).items() if status == "completed"]

    # Organize projects by status
    projects_ongoing = [project for project in user.get("projects", []) if project.get("status") == "ongoing"]
    projects_completed = [project for project in user.get("projects", []) if project.get("status") == "completed"]

    # Pass organized data to the template
    return render_template(
        "dashboard.html",
        user=user,
        skills_ongoing=skills_ongoing,
        skills_completed=skills_completed,
        projects_ongoing=projects_ongoing,
        projects_completed=projects_completed
    )


@app.route('/add-member', methods=['POST'])
def add_member():
    logged_in_user_email = session.get('user_email')
    if not logged_in_user_email:
        return jsonify({'success': False, 'message': 'Project lead not logged in'})

    data = request.json
    email = data.get('email')
    project_index = int(data.get('projectIndex'))  # Make sure this is treated as an integer

    # Log incoming data
    print(f"Logged-in user email: {logged_in_user_email}")
    print(f"Requested email to add: {email}")
    print(f"Project index: {project_index}")

    # Fetch the logged-in user's data
    user = mongo.db.users.find_one({"email": logged_in_user_email})
    if not user:
        return jsonify({'success': False, 'message': 'Logged-in user not found'})

    # Find the ongoing project with the matching project_index
    project = next((p for p in user.get('projects', []) if p.get('status') == 'ongoing' and p.get('project_index') == project_index), None)

    if not project:
        return jsonify({'success': False, 'message': 'Project not found or invalid project index'})

    project_name = project['project_name']

    # Update the project to add the new member
    update_result = mongo.db.users.update_one(
        {"email": logged_in_user_email, "projects.project_index": project_index},
        {"$addToSet": {"projects.$.members": email}}  # $addToSet prevents duplicate entries
    )

    if update_result.modified_count == 1:
        return jsonify({'success': True, 'message': 'Member added successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Failed to update project. Please try again.'})

# Helper function to normalize the name by removing spaces and making it case-insensitive
def normalize_name(name):
    return re.sub(r'\s+', '', name.strip()).lower()

# Function to preprocess and normalize college names
def preprocess_college_names():
    for college in mongo.db.colleges.find():
        normalized_name = normalize_name(college.get("college_name", ""))
        mongo.db.colleges.update_one(
            {"_id": college["_id"]},
            {"$set": {"normalized_name": normalized_name}}
        )

# Helper function to validate college name
def validate_college_name(college_name):
    if not college_name or not college_name.strip():
        return False
    normalized_name = normalize_name(college_name)
    is_valid_college = mongo.db.colleges.find_one(
        {"normalized_name": normalized_name}
    )
    return bool(is_valid_college)

# Endpoint to validate college name
@app.route("/validate-college", methods=["GET"])
def validate_college():
    college_name = request.args.get("name", "").strip()
    if validate_college_name(college_name):
        return jsonify({"valid": True})
    else:
        return jsonify({"valid": False})

@app.route("/update_user", methods=["POST"])
def update_user():
    user_email = session.get("user_email")
    if not user_email:
        return jsonify({"success": False, "message": "User not logged in"}), 403

    updated_data = request.json

    # Fetch the existing user document
    user = mongo.db.users.find_one({"email": user_email})
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # Prepare fields to update only if they exist in the user's document
    fields_to_update = {}

    # Update GitHub and LinkedIn URLs in social_media_links dictionary
    if "social_media_links.github" in updated_data:
        github_url = updated_data["social_media_links.github"]
        fields_to_update["social_media_links.github"] = github_url

    if "social_media_links.linkedin" in updated_data:
        linkedin_url = updated_data["social_media_links.linkedin"]
        fields_to_update["social_media_links.linkedin"] = linkedin_url

    # Update only valid fields
    if fields_to_update:
        mongo.db.users.update_one({"email": user_email}, {"$set": fields_to_update})
        return jsonify({"success": True, "message": "User details updated successfully"})
    else:
        return jsonify({"success": False, "message": "No valid fields to update"}), 400



@app.route('/add_project', methods=['POST'])
def add_project():
    try:
        # Retrieve logged-in user's email from the session
        user_email = session.get("user_email")  # Access session["user_email"]

        if not user_email:
            return jsonify({"error": "User is not logged in"}), 401  # Unauthorized error

        # Parse the form data from the request
        data = request.json

        # Validate and process skills as a list
        skills = data.get('skills', [])
        if not isinstance(skills, list):
            return jsonify({"error": "Skills must be provided as a list."}), 400

        # Validate GitHub link
        github_link = data.get('github_link')
        if not github_link or not github_link.startswith("http"):
            return jsonify({"error": "A valid GitHub link is required."}), 400

        # Get current number of projects to assign project_index
        user = mongo.db.users.find_one({"email": user_email})  # Fetch the user document
        if not user:
            return jsonify({"error": "User not found."}), 404
        
        current_project_count = len(user.get("projects", []))  # Count existing projects
        project_index = current_project_count + 1  # Index starts from 1

        # Build project details with project_index
        project_details = {
            "project_index": project_index,  # Assign project_index
            "project_name": data.get('project_name'),
            "project_lead_name": data.get('project_lead_name'),
            "description": data.get('description'),
            "skills": skills,  # Ensure skills are stored as an array
            "city": data.get('city'),
            "github_link": github_link,  # Include GitHub link in project details
            "status": data.get('status', 'ongoing'),  # Default status is 'ongoing'
            "members": []  # Initialize an empty array for members
        }

        # Update the user's document in MongoDB by adding the new project
        result = mongo.db.users.update_one(
            {"email": user_email},  # Find the user by logged-in email
            {"$push": {"projects": project_details}}  # Add the project to the 'projects' array
        )

        # Check if the user was updated
        if result.modified_count > 0:
            return jsonify({"message": "Project added successfully!"}), 200
        else:
            return jsonify({"error": "Project not added."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/project') 
def project():
    # Fetching all the users from the MongoDB 'users' collection
    users_collection = mongo.db.users
    projects_data = []

    # Retrieving the projects from the database
    for user in users_collection.find():
        for project in user.get('projects', []):
            project_data = {
                'id': str(user['_id']),  # Add user ID for fetching lead details
                'name': project['project_name'],
                'lead': project['project_lead_name'],
                'description': project['description'],
                'skills': project.get('skills', []),  # Pass the array directly
                'city': user.get('city', ''),
                'leadEmail': user.get('email', ''),
                'github_link': project.get('github_link', 'N/A')  # Include GitHub link
            }
            projects_data.append(project_data)

    return render_template('project.html', projects=projects_data)



@app.route('/project/lead/<project_id>', methods=['GET'])
def get_lead_details(project_id):
    # Fetch the lead details for the selected project
    users_collection = mongo.db.users
    try:
        user = users_collection.find_one({"_id": ObjectId(project_id)})
    except Exception as e:
        return jsonify({'error': 'Invalid project ID'}), 400

    if user:
        lead_details = {
            'name': user.get('name'),
            'email': user.get('email'),
            'college': user.get('college'),
            'phone_number': user.get('phone_number'),
            'skills': user.get('skills', {}),
            'projects': [project['project_name'] for project in user.get('projects', [])],
            'city': user.get('city'),
            'state': user.get('state'),
            'github': user.get('social_media_links', {}).get('github', ''),
            'linkedin': user.get('social_media_links', {}).get('linkedin', '')
        }
        return jsonify(lead_details)
    else:
        return jsonify({'error': 'Lead not found'}), 404


@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        # Get data from the request
        recipient_email = request.json.get('email')  # Email of the user to receive the message
        subject = request.json.get('subject')
        message = request.json.get('message')

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS  # Your email address (sender)
        msg['To'] = recipient_email  # The recipient's email (user's email)
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient_email, msg.as_string())

        return jsonify({"status": "success", "message": "Email sent successfully!"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to send email: {str(e)}"}), 500


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear all session data
    return jsonify({"success": True, "message": "Logged out successfully"}), 200

if __name__ == "__main__":
     preprocess_college_names()
     app.run(debug=True, host="localhost")
