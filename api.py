import os
import requests
from dotenv import load_dotenv

class API:
    def __init__(self):
        load_dotenv()
        
        self.api_key = os.getenv("API_KEY")
        self.stardance_username = os.getenv("STARDANCE_USERNAME")
        self.url = "api.stardancestats.xyz/v1/"
        
    def get_projects(self) -> list:
        return ["stardance"]