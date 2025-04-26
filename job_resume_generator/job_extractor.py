from typing import Dict,Any,Optional
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_openai import OpenAIEmbeddings


class JobExtractor :
    def __init__(self,llm):
        self.llm = llm
        self.embeddings = OpenAIEmbeddings()

    def extract_job_description_from_url(self,url: str) -> str:
        try:
            loader = WebBaseLoader(url)
            docs = loader.load()
            soup = BeautifulSoup(docs[0].page_content,"html.parser")
            selectors = [
            '.job-description',
            '#job-description',
            '.description',
            '#description',
            '.jd',
            '#jd',
            '.job-details',
            '#job-details',
            '.styles_job-desc-container__txpYf'
            ]
            print(f"Job request for {url}")
            print(soup.text)
            for selector in selectors:
                element = soup.select_one(selector)
                if element :
                    return element.get_text(separator='\n',strip=True)
            return soup.get_text(separator='\n',strip=True)
            
        except Exception as e:
            print("Error extracting job description {}",e)
            return ""

    def process_job_description(self,job_description:str) -> Dict[str,Any]:
        prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert resume writer and career coach. Analyze the following job description and extract:
         - Key skills required
         - Technologies mentioned
         - Experience level (entry, mid, senior)
         - Job title
         - Industry
         - Any specific qualifications or certifications mentioned
         
         Return the information in JSON format with the above keys."""),
        ("user", "{input}")
        ])
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({"input": job_description})
        try:
            import json
            return json.loads(result)
        except:
            return {"error": "Could not parse job description analysis"}
        
    

    

