"""
Resource Service for CivicAid
Handles loading, searching, and filtering the local resource database.
"""

import json
from pathlib import Path
from typing import Optional


class ResourceService:
    def __init__(self):
        self.data = self._load_data()
        self.resources = self.data.get("resources", [])
        self.categories = self.data.get("categories", {})
    
    def _load_data(self) -> dict:
        """Load the JSON resource database."""
        data_path = Path(__file__).parent.parent / "data" / "resources.json"
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_all_categories(self) -> dict:
        """Return all categories with metadata."""
        return self.categories
    
    def get_resources_by_category(self, category: str) -> list:
        """Filter resources by category."""
        return [r for r in self.resources if r["category"] == category]
    
    def search_resources(
        self,
        category: Optional[str] = None,
        city: Optional[str] = None,
        service_type: Optional[str] = None,
        query: Optional[str] = None,
        student: Optional[bool] = None
    ) -> list:
        """
        Search resources with multiple filters.
        """
        results = self.resources.copy()
        
        if category:
            results = [r for r in results if r["category"] == category]
        
        if city:
            results = [r for r in results if r["city"].lower() == city.lower()]
        
        if service_type:
            results = [r for r in results if r["type"] == service_type]
        
        if query:
            query_lower = query.lower()
            results = [
                r for r in results
                if query_lower in r["name"].lower()
                or query_lower in r["description"].lower()
                or query_lower in r.get("eligibility", "").lower()
            ]
        
        if student:
            # Prioritize student resources
            student_res = [r for r in results if "student" in r.get("eligibility", "").lower() or "UC Davis" in r.get("name", "")]
            other_res = [r for r in results if r not in student_res]
            results = student_res + other_res
        
        return results
    
    def get_resource_by_id(self, resource_id: str) -> Optional[dict]:
        """Get a single resource by its ID."""
        for r in self.resources:
            if r["id"] == resource_id:
                return r
        return None
    
    def get_crisis_resources(self) -> list:
        """Return emergency/crisis resources that are available 24/7."""
        return [
            r for r in self.resources
            if "24/7" in r.get("hours", "") or "crisis" in r.get("description", "").lower()
            or r["id"] in ["mental-004", "safety-003", "mental-002"]
        ]
