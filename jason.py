import json
import re

def is_valid_json_line(line):
    """
    Check if a line can be parsed as JSON.
    """
    try:
        # Test if line can be treated as part of a valid JSON array
        json.loads(f"[{line.strip()}]")
        return True
    except json.JSONDecodeError:
        return False

def clean_json_file(input_file, output_file):
    """
    Cleans a JSON file by removing problematic lines and saves to a new file.
    """
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            valid_lines = []
            malformed_lines_count = 0

            # Read line by line and validate
            for line_number, line in enumerate(infile, start=1):
                if is_valid_json_line(line):
                    valid_lines.append(line.strip())
                else:
                    malformed_lines_count += 1
                    print(f"Removed malformed line {line_number}: {line.strip()}")

            # Reconstruct the JSON
            cleaned_content = "[\n" + ",\n".join(valid_lines) + "\n]"

            # Validate the entire cleaned content
            try:
                parsed_data = json.loads(cleaned_content)  # Full JSON validation
                json.dump(parsed_data, outfile, indent=4)  # Write to file
                print(f"Cleaned JSON file saved to {output_file}")
                print(f"Total malformed lines removed: {malformed_lines_count}")
            except json.JSONDecodeError as e:
                print(f"Error in final JSON validation: {e}")

    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")

# File paths
input_json_file = "all_engg.json"   # Replace with the actual input file path
output_json_file = "cleaned_college.json"  # Replace with the actual output file path

# Call the function
clean_json_file(input_json_file, output_json_file)
