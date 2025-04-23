# from research_agent 
import research_agent
from compaign_agent import getCompaignCreatorAgent
from digital_marketer import getDigitalMarketingContentCreatorAgent
from tasks import Task

# from langchain.chat_models import ChatOpenAI
from langchain_openai.chat_models import ChatOpenAI
from langchain.agents import load_tools
from langchain.llms import OpenAI
from crewai import Crew,Process
import os 


import warnings
warnings.filterwarnings("ignore")

OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME= 'gpt-3.5-turbo'
llm = ChatOpenAI(model_name=OPENAI_MODEL_NAME,open_api_key=OPENAI_API_KEY)

marketResearchAgent = research_agent.getMarketResearcherAgent(llm)
contentAgent = getDigitalMarketingContentCreatorAgent(llm)
compaignAgent = getCompaignCreatorAgent(llm)

tasks = Task(marketResearchAgent,compaignAgent,contentAgent)
compaigntask = tasks.getCompaignTask()
researchTask = tasks.getResearchTask()
contentTask = tasks.getContentTask()

crew = Crew(
    agents=[marketResearchAgent,compaignAgent,contentAgent],
    tasks=[researchTask,compaigntask,contentTask],
    process=Process.sequential
)

crew.kickoff()
