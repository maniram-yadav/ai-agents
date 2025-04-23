from blog_generater import BlogGenerator
import json
import os


api_key = os.getenv('OPENAI_API_KEY')
url = 'https://towardsdatascience.com/mapreduce-how-it-powers-scalable-data-processing/'

generator = BlogGenerator(api_key)
blog_post = generator.generate_blog_post(url)
with open('generated_blog_post.json','w') as f :
    json.dump(blog_post,f,indent=2)

print("Blog post generation complete")
print(f"Title : {blog_post['title']}")
print(f"Word count : {blog_post['seo_data']['word_count']}")
print(f"SEO Score : {blog_post['seo_data']['seo_score']}")
