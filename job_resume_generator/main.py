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


class JobExtractor :
    def extract_job_description_from_url(url: str) -> str:
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
            '#job-details'
            ]

            for selector in selectors:
                element = soup.select_one(selector)
                if element :
                    return element.get_text(separator='\n',strip=True)
            return soup.get_text(separator='\n',strip=True)
            
        except Exception as e:
            print("Error extracting job description {}",e)
            return ""


