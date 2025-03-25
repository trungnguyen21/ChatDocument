import os
import json
from typing import Dict

class Cache:
    def __init__(self):
        """A class to manage caching of files and associated retrievers and RAG chains.
        The cache is implemented using on-disk storage and maintains a file map in JSON format.
        """
        # Create ./data/files and ./data/vectorstore directories if they don't exist
        if not os.path.exists("data"):
            os.mkdir("data")
        if not os.path.exists("data/files"):
            os.mkdir("data/files")

        self.data_path = "data/files"
        self.file_map_path = "data/file_map.json"

        self.retrievers = {}
        self.rag_chains = {}

        self.file_map: Dict[str, str] = self.load_file_map()

    # Function to load the file map from the JSON file
    def load_file_map(self) -> Dict[str, str]:
        if os.path.exists(self.file_map_path):
            with open(self.file_map_path, "r") as f:
                return json.load(f)
        return {} 
    
    # Function to save the file map to the JSON file
    def save_file_map(self):
        with open(self.file_map_path, "w") as f:
            json.dump(self.file_map, f)

    def get_retrievers(self) -> Dict[str, str]:
        return self.retrievers
    
    def get_rag_chains(self) -> Dict[str, str]:
        return self.rag_chains
    
    def get_file_map(self) -> Dict[str, str]:
        return self.file_map
    
    def get_data_path(self):
        return self.data_path
    
    def get_file_by_id(self, file_id: str):
        return self.file_map.get(file_id)
    
    def get_cached_file(self, file_id: str) -> tuple:
        return self.retrievers.get(file_id), self.rag_chains.get(file_id)
    
    def save_file(self, file_id: str, file_path: str):
        self.file_map[file_id] = file_path
        self.save_file_map(self.file_map)
    
    def delete_file(self, file_id: str):
        file_path = self.file_map.get(file_id)
        if file_path:
            try: 
                os.remove(file_path)
                del self.file_map[file_id]
                self.save_file_map()

                self.retrievers.pop(file_id)
                self.rag_chains.pop(file_id)
                return True
            except Exception as e:
                print(f"Error in deleting file: {e}")
                raise
        return False
    
    def clear_cache(self):
        try: 
            self.retrievers.clear()
            self.rag_chains.clear()
            
            file_names = os.listdir(self.data_path)
            for file in file_names:
                os.remove(os.path.join(self.data_path, file))
                self.file_map.clear()
                self.save_file_map(self.file_map)
            return True
        except Exception as e:
            print(f"Error in clearing cache: {e}")
            raise
    

