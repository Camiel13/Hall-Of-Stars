import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv, set_key

class API:
    def __init__(self):
        load_dotenv()
        
        self.api_key = os.getenv("API_KEY")
        self.stardance_username = os.getenv("STARDANCE_USERNAME")
        self.url = "https://api.stardancestats.xyz/v1"
        self.env_path = Path(".env")
        
    def get_projects(self) -> dict:
        if not self.stardance_username:
            return [
                {"name": "Demo project"},
                {"name": "Demo project"},
                {"name": "Demo project"}
            ]
        
        response = requests.get(
            url=f"{self.url}/users/{self.stardance_username}/projects"
        )
        
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            print(f"Something went wrong while fetching your profile. Code {response.status_code}: {response.text}")
            sys.exit()
            
    def set_username(self, username: str):
        self.stardance_username = username
        set_key(self.env_path, "STARDANCE_USERNAME", username)