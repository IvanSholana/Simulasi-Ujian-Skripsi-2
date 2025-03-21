from app.utils.ai_agent.llm_instance import LLMInstance
from app.utils.vector_database.create_vdb import VectorDatabase
from app.utils.document.split_document import DocumentPreparation
from app.utils.document.extract_abstract import extract_abstract
from app.static.prompts.generate_query import create_query_prompt
from app.static.prompts.generate_question import create_question_prompt
from langchain_openai import OpenAIEmbeddings
import random
from app.utils.audio.text_to_speech import AudioManagement
import json
import datetime
from app.static.prompts.evaluation_answer import evaluation_answer_prompt

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
        self.audio_convert = AudioManagement()
        self.question = ""
    
    def create_question(self):
        random_index = random.randint(0, len(self.list_of_query) - 1)
        selected_query = self.list_of_query[random_index]['query']
        self.context = self.vdb.search(query=selected_query)
        self.question = self.model.invoke(create_question_prompt.format(query=selected_query, title=self.title, context=self.context))
        self.question = json.loads(self.question)['question']
        
        # Generate filename based on timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"audio_question_{timestamp}.mp3"
        
        audio_question_path = self.audio_convert.text_to_speech(file_name=file_name, text=self.question)
        return audio_question_path
    
    def evaluation_answer(self,student_answer):
        current_question = self.question
        evaluation_result = self.model.invoke(evaluation_answer_prompt.format(question=current_question,answer=student_answer))
        result = json.loads(evaluation_result)
        print(result)
        
        quality_answer = result['penilaian']
        quality_reason = result['alasan']
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"audio_evaluation_{timestamp}.mp3"
        
        if quality_answer == 'kurang':
            audio_question_path = self.audio_convert.text_to_speech(file_name=file_name, text=quality_reason)
        
            return {
                'quality_answer' : quality_answer, 
                'quality_reason' : quality_reason,
                'audio_url' : audio_question_path
                }
            
        elif quality_answer == 'cukup':
            return {
                'quality_answer' : quality_answer
                }
        