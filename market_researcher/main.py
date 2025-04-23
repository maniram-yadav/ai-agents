from research_agent import getMarketResearcher
import os 
import openai
# from langchain.chat_models import ChatOpenAI
from langchain_openai.chat_models import ChatOpenAI
from langchain.agents import load_tools
from crewai import Agent,Task,Crew,Process
from langchain.llms import OpenAI


import warnings
warnings.filterwarnings("ignore")

OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME= 'gpt-3.5-turbo'
llm = ChatOpenAI(model_name=OPENAI_MODEL_NAME,open_api_key=OPENAI_API_KEY)
mr = getMarketResearcher(llm)
