import openai
import json
from typing import Dict

class WritingAgent :
    
    def __init__(self,open_ai_key:str):
        openai.api_key = open_ai_key

    def expand_section(self, section: str, context: Dict) -> str:
        prompt = f"""  Write a detailed blog post section about: {section}
        Context from source: {context['main_text'][:1000]}
        Target audience: Blog readers interested in {context['title']}
        Tone: Professional but conversational
        Length: 300-500 words
        Include:
        - Clear explanations
        - Examples where appropriate
        - Engaging language
        - Natural keyword incorporation
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    def generate_intro(self,outline:Dict) -> str:

        prompt = f"""
        Write an engaging introduction for a blog post titled : {outline['title']}
        Keywords to inclue {", ".join(outline['keywords'][:3])}
        target word count : 150-200 words

        Make it :
            - Attention-grabbing
            - Clearly state what the post will cover
            - Include a hook to keep readers engaged
        
        """
        response = openai.ChatCompletion.create(
             model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    
    