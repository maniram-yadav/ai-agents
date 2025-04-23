from pdf import Pdf
from agent_chain import create_agent_chain 

class Query:
    def __init__(self,folder=None):
        if folder==None :
            folder = 'pdfs'
        pdf = Pdf(folder)
        self.vectordb =  pdf.load_persist_pdfs()
        self.chain = create_agent_chain()
        
    def get_llm_response(self,query):
        matching_docs = self.vectordb.similarity_search(query)
        answer = self.chain.run(input_documents=matching_docs, question=query)
        return answer


    