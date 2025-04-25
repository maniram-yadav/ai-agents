import os
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


class CodeBaseQATool:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(temprature=0,model="gpt-4")
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.vector_store = None
        self.qa_chain = None
        self.repo_path = None
    
    def load_repository(self,repo_url :Optional[str]=None, local_path:Optional[str]=None):
        if repo_url:
            self._load_from_github(repo_url)
        elif local_path:
            self._load_from_local(local_path)
        else :
            raise ValueError("repo url or local path must be provided")
        

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
        if not os.path.exists(local_path):
            raise ValueError(f"Local path {local_path} does not exist")
        from langchain.document_loaders import DirectoryLoader
        loader = DirectoryLoader(
            local_path,
            glob="**/*",
            silent_errors=True,
            loader_kwargs={"autodetect_encoding": True}
        )
        documents = loader.load()
        self._process_documents(documents)
        self.repo_path = local_path

    def _should_load_file(self,file_path:str)-> str:
        excluded_dirs = {".git", "__pycache__", "node_modules", "venv", "dist", "build"}
        excluded_extensions = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".pdf"}
        if any(part in excluded_dirs for part in file_path.split(os.sep)):
            return False
        if os.path.splitext(file_path)[1] in excluded_extensions:
            return False
        return True


    def _process_documents(self, documents: List):
        code_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON,
            chunk_size=1000,
            shunk_overlap=200
        )
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
            )
        split_docs = []
        for doc in documents:
            if doc.metadata.get("file_path","").endswith(".py"):
                split_docs.extend(code_splitter.split_documents([doc]))
            else :
                split_docs.extend(text_splitter.split_documents([doc]))
        self.vector_store = Chroma.from_documents(split_docs,self.embeddings)
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            self.llm,
            self.vector_store.as_retriever(),
            memory=self.memory
            )
        

    def ask_question(self, question: str) -> str:
        if not self.qa_chain :
            raise ValueError("No repository loaded. Please laod a repositor first")
        result = self.qa_chain({"question":question})
        return result["answer"]
        
    def get_codebase_overview(self) -> str:
        if not self.qa_chain :
            raise ValueError("no repo loaded, load the repo first")
        prompt = """Please provide a comprehensive overview of this codebase, including:
        1. The apparent purpose of the project
        2. Key modules or components
        3. Notable architectural patterns
        4. Entry points or main execution flows
        5. Any obvious dependencies
        6. Recommendations for where a new contributor should start looking"""
        return self.ask_question(prompt)
    
        
    def get_contribution_guidance(self) -> str:
        
        if not self.qa_chain:
            raise ValueError("No repository loaded. Please load a repository first.")
                
        prompt = """Based on the codebase structure and content, provide specific guidance for:
        1. Common contribution opportunities (e.g., areas needing tests, documentation)
        2. Code style and conventions observed
        3. Testing approach and how to add new tests
        4. Documentation standards
        5. Any contribution processes evident from the repository files"""
        
        return self.ask_question(prompt)

    def main():
        pass


        

