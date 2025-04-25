import os
from dotenv import load_dotenv
from langchain.document_loaders import GitLoader
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from typing import List, Optional
import tempfile
import shutil
import argparse

load_dotenv()

class CodeBaseQATool:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(temprature=0,model="gpt-4")
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.vector_store = None
        self.qa_chain = None
        self.repo_path = None
    
    def load_repository(self,repo_url :Optional[str]=None, local_path:Optional[str]=None):
        # if repo_url:
        pass

    def _load_from_github(self,repo_url:str):
        temp_dir = tempfile.mkdtemp()
        try :
            loader = GitLoader(
                clone_url=repo_url,
                repo_path=temp_dir,
                branch="main",
                file_filter=lambda file_path : self._should_load_file(file_path)
            )
            documents = loader.load()
            self._process_documents(documents)
            self.repo_path = temp_dir

        except Exception as e:
            shutil.rmtree(temp_dir)
            raise e

    def _load_from_local(self, local_path: str):
        pass
    def _should_load_file(self,file_path:str)-> str:
        excluded_dirs = {".git", "__pycache__", "node_modules", "venv", "dist", "build"}
        excluded_extensions = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".pdf"}
        if any(part in excluded_dirs for part in file_path.split(os.sep)):
            return False
        if os.path.splitext(file_path)[1] in excluded_extensions:
            return False
        return True

    def _process_documents(self, documents: List):
        pass
    def ask_question(self, question: str) -> str:
        pass
    def get_codebase_overview(self) -> str:
        pass
    def get_contribution_guidance(self) -> str:
        pass
    def main():
        pass


        

