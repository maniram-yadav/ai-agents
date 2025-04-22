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

    
        
  