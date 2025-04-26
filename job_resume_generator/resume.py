import os
from typing import Dict,Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class Resume:
    def __init__(self,llm):
        self.llm = llm

    def generate_tailored_resume(self,job_info:Dict[str,Any],candidate_info:Dict[str,Any]) -> str:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a professional resume writer. Create a tailored resume for a candidate based on the job requirements and their background.
         
         Job Information:
         {job_info}
         
         Candidate Background:
         {candidate_info}
         
         Guidelines:
         1. Highlight the candidate's most relevant experiences first
         2. Match the language and keywords from the job description
         3. Focus on quantifiable achievements
         4. Keep it concise (1-2 pages max)
         5. Use a professional format with clear sections
         6. Include only information relevant to this specific job
         
         Structure the resume with these sections:
         - Contact Information
         - Professional Summary
         - Skills (tailored to the job)
         - Professional Experience (most relevant first)
         - Education
         - Any relevant certifications or projects"""),
            ("user", "Please generate the tailored resume now.")
            ])
        chain = prompt_template | self.llm | StrOutputParser()
        return  chain.invoke({
            "job_info": str(job_info),
            "candidate_info": str(candidate_info)
            })
    def get_candidate_info() -> Dict[str, Any]:
        
        print("Please provide some information about yourself to generate a tailored resume.")
        candidate_info = {
            "name": input("Full Name: "),
            "email": input("Email: "),
            "phone": input("Phone: "),
            "current_title": input("Current/Most Recent Job Title: "),
            "experience_years": input("Years of Professional Experience: "),
            "skills": input("List your key skills (comma separated): ").split(','),
            "education": input("Highest Education Degree: "),
            "work_history": [],
            "projects": [],
            "certifications": input("Any relevant certifications (comma separated, leave blank if none): ").split(',')
        }
    
        # Add work history
        while True:
            add_job = input("Would you like to add a job to your work history? (yes/no): ").lower()
            if add_job != 'yes':
                break
                
            job = {
                "title": input("Job Title: "),
                "company": input("Company Name: "),
                "duration": input("Duration (e.g., 2018-2022): "),
                "responsibilities": input("Key responsibilities (comma separated): ").split(','),
                "achievements": input("Key achievements (comma separated): ").split(',')
            }
            candidate_info["work_history"].append(job)
        while True:
            add_project = input("Would you like to add a project? (yes/no): ").lower()
            if add_project != 'yes':
                break
            project = {
                'name' : input('Project Name : '),
                'description' : input('Project Description : '),
                "technologies": input("Technologies used (comma separated): ").split(','),
                "outcomes": input("Key outcomes/results: ")
            }
            candidate_info["projects"].append(project)
        return candidate_info
    

    
  