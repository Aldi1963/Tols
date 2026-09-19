"""
Base classes for country-specific document generators
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from pathlib import Path
import random


class CountryGenerator(ABC):
    """Base class for country-specific document generators"""
    
    def __init__(self):
        self.schools = self._load_schools()
        self.first_names = self.get_first_names()
        self.last_names = self.get_last_names()
        self.positions = self.get_positions()
    
    @abstractmethod
    def get_country_name(self) -> str:
        """Return the country name"""
        pass
    
    @abstractmethod
    def get_country_code(self) -> str:
        """Return the country code (e.g., 'uk', 'france')"""
        pass
    
    @abstractmethod
    def get_schools_data(self) -> List[Dict]:
        """Return list of schools"""
        pass
    
    @abstractmethod
    def get_first_names(self) -> List[str]:
        """Return list of first names"""
        pass
    
    @abstractmethod
    def get_last_names(self) -> List[str]:
        """Return list of last names"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[str]:
        """Return list of teaching positions"""
        pass
    
    @abstractmethod
    def get_document_types(self) -> List[str]:
        """Return list of available document types"""
        pass
    
    @abstractmethod
    def generate_document(self, doc_type: str, first: str, last: str, 
                         school: Dict, position: str, dob: str) -> bytes:
        """Generate a specific document type"""
        pass
    
    def _load_schools(self) -> List[Dict]:
        """Load schools from JSON or return default data"""
        data_dir = Path(__file__).parent.parent.parent / "data"
        json_path = data_dir / f"{self.get_country_code()}_schools.json"
        
        if json_path.exists():
            try:
                import json
                return json.loads(json_path.read_text())
            except:
                pass
        
        return self.get_schools_data()
    
    def random_school(self) -> Dict:
        """Get a random school"""
        return random.choice(self.schools)
    
    def search_school(self, query: str) -> Dict:
        """Search for a school by name"""
        query_lower = query.lower()
        for school in self.schools:
            if query_lower in school["name"].lower():
                return school
        return None
    
    def list_schools(self) -> List[str]:
        """List all school names"""
        return [s["name"] for s in self.schools]
    
    def generate_name(self) -> Tuple[str, str]:
        """Generate a random name"""
        return random.choice(self.first_names), random.choice(self.last_names)
    
    def random_position(self) -> str:
        """Get a random teaching position"""
        return random.choice(self.positions)
