from crewai import Agent

def getMarketResearcher(llm) :
    market_researcher = Agent(
        role='Market researcher',
        goal = '',
        backstory = '',
        verbose = True,
        allow_delegation=False,
        llm = llm
    )
    return market_researcher