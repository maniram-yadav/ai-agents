import openai
import json
from typing import Dict,List
import re

class SEOAgent :
    
    def __init__(self,open_ai_key:str):
        openai.api_key = open_ai_key

    def optimize_content(self,content:str,keywords : List[str]) -> Dict:
        word_count = len(content.split())
        keyword_density =  {
            kw : (content.lower().count(kw.lower()))/word_count*100
            for kw in keywords
        }
        meta_prompt = f"""Create an SEO-optimized meta description (max 160 chars) for this content:
        {content[:500]}
        Primary keyword: {keywords[0]}
        """
        meta_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": meta_prompt}],
            temperature=0.5
        )
        meta_description = meta_response.choices[0].message.content[:160]

        title = content.split('\n')[0].replace(' ','-').lower()
        slug = re.sub(r'[^a-z0-9]','',title)[:60]

        return {
             'keyword_density': keyword_density,
            'meta_description': meta_description,
            'slug': slug,
            'word_count': word_count,
            'seo_score': 1
            # 'seo_score':    analyze_seo(content, keywords) 
        }

