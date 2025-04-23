from crewai import Agent

def getMarketResearcherAgent(llm) :
    market_researcher = Agent(
        role='Market researcher',
        goal='Research new and emerging trends in pet products industry in Germany',
        backstory = 'You are a market researcher in the pet product industry',
        verbose = True,
        allow_delegation=False,
        llm = llm
    )
    return market_researcher