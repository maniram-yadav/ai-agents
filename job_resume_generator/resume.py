import os
from typing import Dict,Any,Optional
import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


class Resume:
    def __init__(self,llm):
        self.llm = llm

    def generate_tailored_resume(self,job_info:Dict[str,Any],candidate_info:Dict[str,Any]) -> str:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a professional resume writer. Create a tailored resume for a candidate based on the job requirements and their background.
         
         Job Information:
         {job_info}
         
         Candidate Background:
         {candidate_info}
         
         Guidelines:
         1. Highlight the candidate's most relevant experiences first
         2. Match the language and keywords from the job description
         3. Focus on quantifiable achievements
         4. Keep it concise (1-2 pages max)
         5. Use a professional format with clear sections
         6. Include only information relevant to this specific job
         
         Structure the resume with these sections:
         - Contact Information
         - Professional Summary
         - Skills (tailored to the job)
         - Professional Experience (most relevant first)
         - Education
         - Any relevant certifications or projects"""),
            ("user", "Please generate the tailored resume now.")
            ])
        chain = prompt_template | self.llm | StrOutputParser()
        return  chain.invoke({
            "job_info": str(job_info),
            "candidate_info": str(candidate_info)
            })
    