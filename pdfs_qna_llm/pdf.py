import os
from dotenv import load_dotenv

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
import chromadb

class Pdf :
    def __init__(self,folder):
        self.folder=folder
    
    def load_persist_pdfs(self) -> Chroma :
        documents = []
        for file in os.listdir(self.folder) :
            if file.endswith(".pdf") :
                pdf_path = os.path.join(self.folder,file)
                loader = PyPDFLoader(pdf_path)
                documents.extend(loader.load())
        if documents.count==0 :
            print("No pdf document found in given folder")

        print("All PDF loaded")
        text_splitter = CharacterTextSplitter(chunk_size=1000,chunk_overlap=10)
        chunked_documents = text_splitter.split_documents(documents)
        client = chromadb.Client()
        if client.list_collections():
            consent_colections = client.create_collection("consent_collection")
        else :
            print("Collection already exists")
        vectordb = Chroma.from_documents(
            documents=chunked_documents,
            embedding=OpenAIEmbeddings(),
            persist_directory=os.getcwd()
        )
        vectordb.persist()
        return vectordb