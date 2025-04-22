import requests
from bs4 import BeautifulSoup
import openai
import json
from typing import Dict,List,Optional
import re
from research_agent import ResearchAgent
from content_strategy_agent import ContentStrategyAgent
from performance_agent import PerformanceAgent
from seo_agent import SEOAgent
from visual_agent import VisualAgent
from writing_agent import WritingAgent

class BlogGenerator :
    
    def __init__(self,open_api_key):
        self.research_agent = ResearchAgent()
        self.strategy_agent = ContentStrategyAgent()
        self.writing_agent = WritingAgent()
        self.seo_agent = SEOAgent()
        self.visual_agent = VisualAgent()
        self.performance_agent = PerformanceAgent()

    def generate_blog_post(self,url:str) -> Dict:
        print(f"Analyzing Url : {url} ")
        research_data =self.research_agent.analyze_url(url)
        print("Creating content strategy")
        outline = self.strategy_agent.generate_outline(research_data)
        print("Writing content...")
        sections = {
            'introduction':self.writing_agent.generate_intro(outline),
            'main_content':[
                {'heading': section, 'content':self.writing_agent.expand_section(section,research_data)}
                    for section in outline['sections'] 
                    ],
            'conclusion':self.writing_agent.generate_conclusion(outline)
        }
        
        full_text = f"# {outline['title']}\n\n{sections['introductions']}\n\n"
        full_text += '\n\n'.joiin(
            f"##{s['heading']}\n\n{s['content']}" for s in sections['main_content']
        )
        full_text += f"\n\n## Conclusion\n\n{sections['conclusion']}"

        print("Optimizing for SEO...")
        seo_data = self.seo_agent.optimize_content(full_text,outline['keywords'])

        print("Generating impage prompts....")
        image_prompts = self.visual_agent.generate_image_prompts({
            'title': outline['title'],
            'sections': [s['heading'] for s in sections['main_content']]
        })

        print("Analyzing performance...")
        performance = self.performance_agent.analyze_performance({
            'full_text':full_text,**sections},
            seo_data
        })
        return {
            'title': outline['title'],
            'content': full_text,
            'structure': sections,
            'seo_data': seo_data,
            'image_prompts': image_prompts,
            'performance': performance,
            'keywords': outline['keywords']
        }