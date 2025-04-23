import openai
import json
from typing import Dict

class VisualAgent :
    
    def __init__(self):
        pass

    def generate_image_prompt(self,content:Dict) -> Dict:
        prompt = f"""Based on this blog content, create 3 detailed image prompts for DALL-E/Midjourney:
        Title: {content['title']}
        Main sections: {', '.join(content['sections'])}
        
        Provide:
        1. Featured image prompt (for thumbnail)
        2. Infographic prompt
        3. Section illustration prompt

        return as json with keys : featured,infographics, illustration.
        Each prompt should be detailed (1-2 sentences) and include style guidance.
        """

        response  = openai.chat.completions.create(
            model="gpt-4o",
            # model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                'featured':f"featured images for {content['title'] }, digital art style",
                'infographic': f"Infographic summarizing {content['title']}, clean vector style",
                'illustration': f"Conceptual illustration for {content['sections'][0]}, isometric 3d style"
            }

