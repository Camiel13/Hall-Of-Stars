import os
from dotenv import load_dotenv
import requests

class API:
    def __init__(self):
        load_dotenv()
        
        self.api_key = os.getenv("API_KEY")
        self.stardance_username = os.getenv("STARDANCE_USERNAME")
        
    def get_projects(self) -> list:
        return ["Hall of Stars", "Monicraft", "The Wandering Modder"]