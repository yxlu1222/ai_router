import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("UCLOUD_API_KEY")
api_base = os.getenv("UCLOUD_API_BASE")

print(f"Base URL: {api_base}")

try:
    # Most OpenAI compatible APIs invoke /v1/models (sometimes just /models if not in base path)
    # The base url in env usually has /v1 in it or not. 
    # Let's inspect the base url first in the output, then try to hit the models endpoint.
    if not api_base:
        print("UCLOUD_API_BASE is not set")
        exit(1)
        
    url = api_base.rstrip('/') + "/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"Requesting: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("Models available:")
        for model in data.get('data', []):
            print(f"- {model.get('id')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

except Exception as e:
    print(f"Exception: {e}")
