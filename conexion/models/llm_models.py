from keybert import KeyBERT
from torch import bfloat16
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from torch import cuda
from base_model import BaseModel

class KeyBERTEntities(BaseModel):
    
    def __init__(self):
        self.keybert_model = KeyBERT()

    def fit(self, abstracts: List[str], keyphrases: List[List[str]]) -> None:
        pass

    def predict(self, abstracts: List[str]) -> List[List[str]]:        
        # Extract keywords using KeyBERT entities
        entities = []
        for abstract in abstracts:
            keybert_keywords = [keyword[0] for keyword in self.keybert_model.extract_keywords(abstract, keyphrase_ngram_range=(1, 3), stop_words='english')] #keyphrase_ngram_range=(1, 3),
            entities.append(keybert_keywords)
        
        return entities

class Llama2ZeroShotEntities(BaseModel):
    
    def __init__(self):
        model_id = 'meta-llama/Llama-2-7b-chat-hf'
        device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'
        bnb_config = transformers.BitsAndBytesConfig(
            load_in_4bit=True,  # 4-bit quantization
            bnb_4bit_quant_type='nf4',  # Normalized float 4
            bnb_4bit_use_double_quant=True,  # Second quantization after the first
            bnb_4bit_compute_dtype=bfloat16  # Computation type
        )
        
        model_id = "meta-llama/Llama-2-7b-chat-hf"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = transformers.AutoModelForCausalLM.from_pretrained(
                        model_id,
                        trust_remote_code=True,
                        quantization_config=bnb_config,
                        device_map='auto',
                    )
        model.eval()

        generator = pipeline(
            "text-generation",
            model=model, tokenizer=tokenizer, max_new_tokens=100, temperature=0.1,
            model_kwargs={"torch_dtype": torch.float16, "use_cache": False}  # Adjusted to suit LLaMA model specifics
        )

        # System prompt describes information given to all conversations
        system_prompt = """
        <s>[INST] <<SYS>>
        You are a helpful, respectful and honest assistant for extracting keyphrases related to computer science from provided documents.
        <</SYS>>
        """

        example_prompt = """
        I have a topic that contains the following documents:
        - The development of machine learning algorithms for data analysis involves complex computational techniques and models such as neural networks, decision trees, and ensemble methods, which are used to enhance pattern recognition and predictive analytics.

        Give me all the keyphrases that are present in this document and related to computer science and separate them with commas.
        Make sure you only return the keyphrases and say nothing else. For example, don't say:
        "Sure, I'd be happy to help! Based on the information provided in the document".
        [/INST] machine learning algorithms,data analysis,complex computational techniques,neural networks, decision trees,ensemble methods,pattern recognition,predictive analytics,
        """

        main_prompt = """
        [INST]
        I have the following document:
        [DOCUMENT]

        Give me all the keyphrases that are present in this document and related to computer science and separate them with commas.
        Make sure you only return the keyphrases and say nothing else. For example, don't say:
        "Sure, I'd be happy to help! Based on the information provided in the document".
        [/INST]
        """

        prompt = system_prompt +  main_prompt
        prompt = system_prompt + example_prompt + main_prompt
        llm = TextGeneration(generator, prompt=prompt)
        self.kw_model = KeyBERT(llm=llm, model='BAAI/bge-small-en-v1.5')

    def fit(self, abstracts: List[str], keyphrases: List[List[str]]) -> None:
        pass

    def predict(self, abstracts: List[str]) -> List[List[str]]:        
        # Extract keywords using llama2 entities
        entities = []
        for abstract in abstracts:
            raw_keywords = self.kw_model.extract_keywords([abstract], threshold=0.5)[0]
            cleaned_keywords = [keyword.rstrip('.') for keyword in raw_keywords if keyword.rstrip('.').lower() in abstract.lower()]
            entities.append(cleaned_keywords)
        
        return entities