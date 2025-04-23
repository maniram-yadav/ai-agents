import requests
from bs4 import BeautifulSoup
from typing import Dict

class ResearchAgent :
    
    def __init__(self):
        self.headers = {
            'User-Agent' :  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def analyze_url(self,url:str) -> Dict:
        
        try :
            response = requests.get(url,headers=self.headers)
            soup = BeautifulSoup(response.text,'html.parser')
            paragraphs = [p.get_text().strip() for p in soup.find_all('p')]
            headings = [h.get_text().strip() for h in soup.find_all(['h1','h2','h3'])]

            title = soup.title.string if soup.title else ""
            meta_description = soup.find('meta',attrs={'name':'description'})
            meta_description = meta_description['content'] if meta_description else ""
            
            return {
                'title':title,
                'meta_description':meta_description,
                'headings':headings,
                'paragraphs':paragraphs,
                'main_text':' '.join(paragraphs),
                'url':url
            }


        except Exception as e :
            print(f"Error analyzing Url : {e}") 
            return {}



