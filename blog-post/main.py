from research_agent import ResearchAgent
from blog_generater import BlogGenerator
import json

OPEN_API_KEY = ""
url = 'https://medium.com/design-bootcamp/top-10-ai-agents-in-2025-db41e98a4a68'

generator = BlogGenerator(OPEN_API_KEY)
blog_post = generator.generate_blog_post(url)
with open('generated_blog_post.json','w') as f :
    json.dump(blog_post,f,indent=2)

print("Blog post generation complete")
print(f"Title : {blog_post['title']}")
print(f"Word count : {blog_post['seo_data']['word_count']}")
print(f"SEO Score : {blog_post['seo_data']['seo_score']}")


researchAgent = ResearchAgent()
data = researchAgent.analyze_url('https://medium.com/design-bootcamp/top-10-ai-agents-in-2025-db41e98a4a68')
print(data)