import openai
import json
from typing import Dict,List
import re


class PerformanceAgent:
    def analyze_performance(self,content:Dict,seo_data:Dict)-> Dict :
        avg_sequence_length = sum( len(s.split()) for s in content['full_text'].split('.') )/ len(
            content['full_text'].split('.'))
        readability = max(0,min(100,100-avg_sequence_length-10*2))
        engagement = min(100,seo_data['word_count']/3+readability/2)
        return {
             'readability_score': readability,
            'engagement_score': engagement,
            'recommendations': self.generate_recommendations(content, seo_data)
        }