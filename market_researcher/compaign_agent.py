from crewai import Agent

def getCompaignCreator(llm) :
    compaign_creator = Agent(
        role='Marketing Campaign Creator',
        goal='Come up with 3 interesting marketing campaign ideas in the pet product industry based on market research insights',
        backstory = 'You are a marketing campaign planner in the pet product industry',
        verbose = True,
        allow_delegation=False,
        llm = llm
    )
    return compaign_creator