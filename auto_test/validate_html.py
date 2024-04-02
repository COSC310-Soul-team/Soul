import requests
from glob import glob

def validate_html(file_path):
    files = {'file': open(file_path, 'rb')}
    response = requests.post("https://validator.w3.org/nu/", files=files, params={"out": "json"})
    response_json = response.json()

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
