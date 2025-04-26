from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from book_recommender import BookRecommender
from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder


class EnhancedBookRecommender(BookRecommender):
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

        