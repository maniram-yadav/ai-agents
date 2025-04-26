from job_extractor import JobExtractor
from resume import Resume
from typing import Any
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
jobExtractor = JobExtractor(llm)
resume = Resume(llm)

def main():
    print("Job Description to Resume Generator")
    print("----------------------------------")
    
    input_method = input("Do you have a job URL or job description text? (url/text): ").lower()
    if input_method == 'url':
        url = input("Enter the job posting URL: ")
        job_description = jobExtractor.extract_job_description_from_url(url)
    else:
        print("Paste the job description (press Enter then Ctrl+D when finished):")
        job_description = ""
        while True:
            try:
                line = input()
            except EOFError:
                break
            job_description += line + "\n"
        
    if not job_description.strip():
        print("Error: No job description provided.")
        return
    print("\nAnalyzing job description...")
    job_info = jobExtractor.process_job_description(job_description)
    if "error" in job_info:
        print("Failed to analyze job description.")
        return
    print(f"\nDetected Job Title: {job_info.get('job_title', 'Unknown')}")
    print(f"Key Skills: {', '.join(job_info.get('key_skills', []))}")
    
    candidate_info = resume.get_candidate_info()
    print("\nGenerating your tailored resume...")
    resume = resume.generate_tailored_resume(job_info, candidate_info)
    filename = f"tailored_resume_{candidate_info['name'].replace(' ', '_')}.txt"
    with open(filename, 'w') as f:
        f.write(resume)
    print(f"\nSuccess! Your tailored resume has been saved as {filename}")
    print("\n=== GENERATED RESUME ===\n")
    print(resume)
    
if __name__=="__main__":
    main()

    
  