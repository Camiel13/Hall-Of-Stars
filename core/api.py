import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv, set_key
from concurrent.futures import ThreadPoolExecutor

class API:
    def __init__(self):
        load_dotenv()
        
        self.api_key = os.getenv("API_KEY")
        self.stardance_username = os.getenv("STARDANCE_USERNAME")
        self.env_path = Path(".env")
        
        self.url = "https://api.stardancestats.xyz/v1"
        self.session = requests.Session()
        
        self.projects = None
        
    def get_projects(self) -> dict:
        self.projects = [
            {
                "_id": "0",
                "title": "Demo project",
                "owner_username": "Stardancer",
                "is_super_star": False,
                "stats": {
                    "total_hours": 10.0,
                    "stardust_total": 100,
                    "rank_hours": 500,
                    "rank_stardust": 250,
                    "likes": 5,
                    "views": 42
                }
            },
            {
                "_id": "0",
                "title": "Demo project",
                "owner_username": "Stardancer",
                "is_super_star": False,
                "stats": {
                    "total_hours": 22.0,
                    "stardust_total": 333,
                    "rank_hours": 779,
                    "rank_stardust": 250,
                    "likes": 5,
                    "views": 42
                }
            },
            {
                "_id": "0",
                "title": "Demo project",
                "owner_username": "Stardancer",
                "is_super_star": True,
                "stats": {
                    "total_hours": 39.0,
                    "stardust_total": 577,
                    "rank_hours": 901,
                    "rank_stardust": 454,
                    "likes": 5,
                    "views": 42
                }
            }
        ]
        
        if not self.stardance_username:
            return self.projects
        
        try:
            response = self.session.get(
                url=f"{self.url}/users/{self.stardance_username}/projects"
            )
            
            if response.status_code == 200:
                self.projects = response.json().get("items", [])
                
                def enrich(project):
                    project["stats"]["rank_hours"] = self.get_rank(project_data=project, metric="total_hours")
                    project["stats"]["rank_stardust"] = self.get_rank(project_data=project, metric="stardust_total")
                    return project
                    
                with ThreadPoolExecutor(max_workers=5) as executor:
                    self.projects = list(executor.map(enrich, self.projects))
                
                return self.projects
            else:
                print(f"Something went wrong while fetching your profile. Code {response.status_code}")
                return self.projects

        except Exception as e:
            print(f"Could not reach API: {e}")
            return self.projects
            
    def set_username(self, username: str):
        self.stardance_username = username
        set_key(self.env_path, "STARDANCE_USERNAME", username)
        
    def get_rank(self, project_data: dict, metric: str = "total_hours") -> int:
        try:
            title = project_data["title"]
            project_id = project_data["_id"]
            
            response = self.session.get(
                url=f"{self.url}/projects/search",
                params={"q": title, "metric": metric, "limit": 10}
            )
            if response.status_code == 200:
                items = response.json().get("items")
                
                # Check if the project ID matches
                for item in items:
                    if item.get("project_id") == project_id:
                        return item.get("rank", 99999)

                # Fallback: check for exact title match
                for item in items:
                    if item.get("title", "").strip().lower() == title.strip().lower():
                        return item.get("rank", 99999)
                
                # Fallback: return first result
                if items:
                    return items[0].get("rank", 99999)
                
                return None
            else:
                print(f"Error code {response.status_code} while fetching rank.")
        except Exception as e:
            print(f"Error while fetching project rank for {title}: {e}")
            
    def get_total_count(self, count_type: str = "projects") -> int:
        if hasattr(self, f"_total_{count_type}") and getattr(self, f"_total_{count_type}") is not None:
            return int(getattr(self, f"_total_{count_type}"))
        
        try:
            response = self.session.get(f"{self.url}/global")
            if response.status_code == 200:
                setattr(self, f"_total_{count_type}", response.json().get("totals").get(count_type))
                return int(getattr(self, f"_total_{count_type}"))
            else:
                print(f"Error code {response.status_code} while fetching {count_type} count.")
        except Exception as e:
            print(f"Error while fetching global {count_type} count: {e}")
        
        # Fallback
        return 60000