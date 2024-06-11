from gensim.models import LdaModel
from gensim.corpora import Dictionary
from base_model import BaseModel

class LDAEntities(BaseModel):
    
    def __init__(self):
        pass

    def fit(self, abstracts: List[str], concepts: List[List[str]]) -> None:
        pass

    def predict(self, abstracts: List[str]) -> List[List[str]]:        
        # Extract keywords using LDA entities
        entities = []
        for abstract in abstracts:
            dictionary = Dictionary([abstract.split()])
            corpus = [dictionary.doc2bow(abstract.split())]
            doc_term_matrix = [dictionary.doc2bow(doc) for doc in [abstract.split()]]
            lda_model = LdaModel(corpus=doc_term_matrix, num_topics=18, id2word=dictionary)  # Adjust the number of topics as needed
            lda_keywords = [word for word, _ in lda_model.show_topic(0)]
            entities.append(lda_keywords)
        
        return entities