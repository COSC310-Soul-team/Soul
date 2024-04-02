import requests
from glob import glob

def validate_html(file_path):
    files = {'file': open(file_path, 'rb')}
    response = requests.post("https://validator.w3.org/nu/", files=files, params={"out": "json"})
    
    # Check the response status code before trying to decode JSON
    if response.status_code != 200:
        print(f"Error validating {file_path}: HTTP {response.status_code}")
        print(response.text)  # This prints the response body which might contain clues about the error
        return False
    
    try:
        response_json = response.json()
    except requests.exceptions.JSONDecodeError as e:
        # Handle JSON decoding errors (e.g., empty responses, responses not in JSON format)
        print(f"Failed to decode JSON response for {file_path}: {e}")
        return False

    if response_json.get("messages"):
        print(f"Validation issues found in {file_path}:")
        for message in response_json["messages"]:
            print(f"- {message.get('message')}")
        return False
    
    return True

def main():
    html_files = glob('**/*.html', recursive=True)
    errors = False
    for file_path in html_files:
        if not validate_html(file_path):
            errors = True
    
    if errors:
        raise Exception("HTML validation failed.")

if __name__ == "__main__":
    main()