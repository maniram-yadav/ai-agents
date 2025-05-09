import openai
import json
from typing import Dict

class ContentStrategyAgent :
    
    def __init__(self):
        pass

    def generate_outline(self,research_data: Dict) -> Dict:
        prompt = f"""Based on the following content from {research_data['url']}, create a detailed blog post outline.
        Main topic: {research_data['title']}
        Key points from source: {research_data['headings'][:5]}
         
        Generate an outline with:
        1. Engaging title (include primary keyword)
        2. Introduction paragraph summary
        3. 4-6 main sections with subheadings (H2s)
        4. Conclusion summary
        5. 5-7 SEO keywords

        Return as JSON with keys: title, introduction, sections, conclusion, keywords.
        """
        response  = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        print(response)
        try :
            return json.loads(response.choices[0].message.content)
        except:
            return {
                'title':research_data['title']+' - Comprehensive guide',
                'introduction': "Introduction generated based on the source content...",
                'sections': [f"Section {i+1}" for i in range(4)],
                'conclusion': research_data['conclusion'],
                'keywords': research_data['keywords']
            }
            
  