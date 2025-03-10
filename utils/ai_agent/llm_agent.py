from utils.ai_agent.llm_instance import LLMInstance
from utils.vector_database.create_vdb import VectorDatabase
from utils.document.split_document import DocumentPreparation
from utils.document.extract_abstract import extract_abstract
from static.prompts.generate_query import create_query_prompt
from static.prompts.generate_question import create_question_prompt
from langchain_openai import OpenAIEmbeddings
import random
import json

class LLM_Agent:
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    def __init__(self,document_path):
        self.model = LLMInstance()
        self.document = DocumentPreparation(data_path=document_path)
        self.vdb = VectorDatabase(collection_name="test-db",document=self.document,embeddings=self.embeddings)
        self.abstract = extract_abstract(split_document=self.document.splited_document)
        self.list_of_query = self.model.invoke(create_query_prompt.format(title=document_path,abstract=self.abstract))
        self.list_of_query = json.loads(self.list_of_query)
        self.title = document_path
    
    def create_question(self):
        random_index = random.randint(0, len(self.list_of_query) - 1)
        selected_query = self.list_of_query[random_index]['query']
        self.context = self.vdb.search(query=selected_query)
        self.question = self.model.invoke(create_question_prompt.format(query=selected_query,title=self.title,context=self.context))
        return self.question