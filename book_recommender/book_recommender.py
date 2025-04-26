import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.llms import Ollama  
from langchain_openai import ChatOpenAI  

# Load environment variables
load_dotenv()

class BookRecommender:
    def __init__(self, model_type="openai"):
          self.model_type=model_type
          if model_type=='openai':
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.7
                )
          else:
              self.llm =Ollama(model='ollama')
          self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert book recommendation system with deep knowledge 
              of literature across all genres and time periods. Your goal is to suggest 
              personalized book recommendations based on the user's preferences."""),
            ("human", """Based on the following information about my reading preferences, 
              suggest 5 books I might enjoy. For each recommendation, include a brief 
              explanation of why you think I would like it.

              My preferences: {user_input}
              
              Please format your response with:
              1. Book Title by Author
              2. Reason for recommendation
              3. ---
              And so on for all 5 recommendations.""")
                ])
          self.recommender_chain = (
            {"user_input": RunnablePassthrough()} 
                | self.prompt_template 
                | self.llm 
                | StrOutputParser()
            )
    def  get_recommendations(self, user_preferences):
        return self.recommender_chain.invoke(user_preferences)    