from typing import Dict,List


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
    def generate_recommendations(self, content: Dict, seo_data: Dict) -> List[str]:
        recs = []
        if seo_data['word-count']<1000:
            recs.append("Consider appending content to 1000+ words for better SEO")
        if any(d < 1.0 for d in seo_data['keywords_destiny'].values()):
            recs.append("Increase keyword density for underutilized keywords")
        if len(content['full_text'].split('\n\n')) < 5 :
            recs.append("Add more paragraph breaks for better readability")
        return recs
    
        
