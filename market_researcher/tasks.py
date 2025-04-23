from crewai import Task

class Task :

    def __init__(self,market_researcher,campaign_creator,digital_marketer):
        self.market_researcher = market_researcher
        self.campaign_creator = campaign_creator
        self.digital_marketer = digital_marketer
        

    def getResearchTask(self):
        research_task = Task(description="What Market Research Task would You like me to do Today?", 
        expected_output = 'New and Emerging Market Trends in the Pet Product Industry in Germany in 2024', 
        agent=self.market_researcher)
        return research_task

    def getCompaignTask(self):
        compaign_task = Task(description="What Marketing Campaigns would You like me to come up with Today?"+
        "Make sure to check with a human if the draft is good before finalizing your answer.", 
        expected_output = 'Digital Marketing Campaign ideas based on the market trends which have the potential to go viral on Instagram, Youtube and Tiktok',
        agent=self.campaign_creator)
        
        return compaign_task
        
    def getContentTask(self):
        digital_marketer_task = Task(description="What Digital Marketing Content would You like me to generate Today?", 
        agent=self.digital_marketer)
        return digital_marketer_task
    