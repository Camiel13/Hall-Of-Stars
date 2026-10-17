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
        projects = [
            {
                "title": "Demo project",
            },
            {
                "title": "Demo project",
            },
            {
                "title": "Demo project"
            }
        ]
        
        if not self.stardance_username:
            return projects
        
        try:
            response = requests.get(
                url=f"{self.url}/users/{self.stardance_username}/projects"
            )
            
            if response.status_code == 200:
                projects = response.json().get("items", [])
                return projects
            else:
                print(f"Something went wrong while fetching your profile. Code {response.status_code}")
                return projects

        except Exception as e:
            print(f"Could not reach API: {e}")
            return projects
            
    def set_username(self, username: str):
        self.stardance_username = username
        set_key(self.env_path, "STARDANCE_USERNAME", username)