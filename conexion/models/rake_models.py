from rake_nltk import Rake
from models.base_model import BaseModel
from typing import List, Tuple

class RakeEntities(BaseModel):
    
    def __init__(self):
        self.rake_nltk_var = Rake()

    def fit(self, abstracts: List[str], concepts: List[List[str]]) -> None:
        pass

    def predict(self, abstracts: List[str]) -> List[List[str]]:        
        # Extract keywords using Rake entities
        entities = []
        for abstract in abstracts:
            self.rake_nltk_var.extract_keywords_from_text(abstract)
            keywords = self.rake_nltk_var.get_ranked_phrases()
            entities.append([(ent, 1.0) for ent in keywords])
        
        return entities