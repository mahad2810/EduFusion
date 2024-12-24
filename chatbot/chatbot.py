import json
import logging
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re  # For cleaning and formatting the response

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="static", static_url_path="/")
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in the environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

# Serve the main HTML file
@app.route("/")
def serve_frontend():
    """Serve the main frontend HTML file."""
    return send_from_directory("static", "ai.html")

@app.route("/study-plan", methods=["POST"])
def generate_study_plan():
    """Generate a study plan dynamically using Gemini API."""
    try:
        data = request.json

        # Input validation
        if not all([data.get("course_name"), data.get("num_days"), data.get("hours_per_day")]):
            logging.error("Missing input fields.")
            return jsonify({"error": "Missing required fields: course_name, num_days, hours_per_day"}), 400

        course_name = data["course_name"]
        num_days = int(data["num_days"])
        hours_per_day = int(data["hours_per_day"])

        # Prepare prompt for Gemini Pro
        prompt = f"""
        You are an AI assistant tasked with creating a daily study plan for learners.

        Course Name: {course_name}
        Days: {num_days}
        Hours per Day: {hours_per_day}

        Plan the topics and subtopics comprehensively, expand content, and make it premium and presentable. 
        Suggest popular paid courses (mention author names) and free YouTube alternatives (include channel names) 
        at the start of the study plan. Avoid using unnecessary symbols like # or * in the output. Use proper 
        indentation and text sizing to differentiate between topics and subtopics.
        """

        logging.debug("Calling Gemini API...")
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        raw_response = response.text

        # Log the raw response for debugging
        logging.debug(f"Raw response from Gemini API: {raw_response}")

        # Check if the response is empty
        if not raw_response.strip():
            logging.error("Empty response from Gemini API.")
            return jsonify({"error": "Empty response from Gemini API."}), 500

        # Format the response into clean HTML
        def clean_and_format_response(text):
            # Remove unnecessary symbols like #, *, etc.
            text = re.sub(r"[#*]", "", text)
            text = text.strip()

            # Convert text into HTML for proper display
            html_output = ""
            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Detect headings or main topics
                if line.startswith("Day") and ":" in line:
                    html_output += f"<h2 style='margin-top: 20px;'>{line}</h2>"
                elif ":" in line:
                    # Subtopics
                    html_output += f"<p style='margin-left: 20px;'>{line}</p>"
                else:
                    # Main topics
                    html_output += f"<h3 style='margin-left: 10px;'>{line}</h3>"
            return html_output

        formatted_response = clean_and_format_response(raw_response)

        # Return the response
        return jsonify({"roadmap": formatted_response})

    except Exception as e:
        logging.error(f"Error generating study plan: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
