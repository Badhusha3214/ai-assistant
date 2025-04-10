import json
import os

class RAGHandler:
    def __init__(self, docs_dir="docs"):
        self.docs_dir = docs_dir
        self.college_data = None
        self.load_college_data()
    
    def load_college_data(self):
        """Load college data from JSON"""
        try:
            with open('college_data.json', 'r') as f:
                self.college_data = json.load(f)
            print("College data loaded successfully")
        except Exception as e:
            print(f"Error loading college data: {e}")
            # Create a minimal placeholder if data is missing
            self.college_data = {
                "institution": {
                    "name": "Kristu Jyoti College",
                    "accreditation": "Academic Institution",
                    "contact": {
                        "email": "info@example.edu",
                        "phone": "123-456-7890"
                    },
                    "departments": [],
                    "facilities": [],
                    "student_services": [],
                    "achievements": []
                }
            }
            print("Created minimal placeholder data")
    
    def generate_rag_prompt(self, query):
        """Generate relevant college information context"""
        if not self.college_data:
            return "No college information available."
            
        query = query.lower()
        info = self.college_data["institution"]
        
        # Extract relevant information based on query keywords
        if any(word in query for word in ["course", "program", "department"]):
            return json.dumps(info["departments"], indent=2)
        elif any(word in query for word in ["facility", "infrastructure"]):
            return json.dumps(info["facilities"], indent=2)
        elif any(word in query for word in ["contact", "email", "phone", "address"]):
            return json.dumps({
                "contact": info["contact"],
                "location": info.get("location", {})
            }, indent=2)
        elif any(word in query for word in ["club", "activity", "service"]):
            return json.dumps(info["student_services"], indent=2)
        elif any(word in query for word in ["achievement", "rank", "grade"]):
            return json.dumps(info["achievements"], indent=2)
        else:
            # Use basic information
            return json.dumps({
                "name": info["name"],
                "accreditation": info["accreditation"]
            }, indent=2)
        
        return ""
