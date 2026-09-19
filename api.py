import os
import sys
import requests
from dotenv import load_dotenv

class API:
    def __init__(self):
        load_dotenv()
        
        self.api_key = os.getenv("API_KEY")
        self.stardance_username = os.getenv("STARDANCE_USERNAME")
        self.url = "https://api.stardancestats.xyz/v1"
        
    def get_projects(self) -> dict:
        response = requests.get(
            url=f"{self.url}/users/{self.stardance_username}/projects"
        )
        
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            print(f"Something went wrong while fetching your profile. Code {response.status_code}: {response.text}")
            sys.exit()