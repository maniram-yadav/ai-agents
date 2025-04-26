from langchain.memory import ConversationBufferMemory
from langchain.chains.conversation.base import ConversationChain
from book_recommender import BookRecommender
from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser


class BufferedBookRecommender(BookRecommender):
    def __init__(self,model_type='openai'):
        super().__init__(model_type)
        self.memory = ConversationBufferMemory()
        self.conversation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert book recommendation assistant. Engage in a conversation 
              to understand the user's reading preferences and suggest personalized books. 
              Ask follow-up questions when needed to refine recommendations."""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        self.conversation_chain = ConversationChain(
            llm = self.llm,
            memory=self.memory,
            prompt = self.conversation_prompt,
            output_parser=StrOutputParser()
         
         )
        
    def chat(self,user_input):
        return self.conversation_chain.invoke({"input": user_input})