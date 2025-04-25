import argparse
from github_qa_tool import CodeBaseQATool
from dotenv import load_dotenv
import os 
import shutil

load_dotenv()

def main() :
    parser = argparse.ArgumentParser(description="Codebase QA and Analysis Tool")
    parser.add_argument("--github", type=str, help="GitHub repository URL")
    parser.add_argument("--local", type=str, help="Local directory path")
    args = parser.parse_args()

    tool = CodeBaseQATool()
    try :
        if args.github :
            print(f"Loading repository from GitHub: {args.github}")
            tool.load_repository(repo_url=args.github)
        elif args.local:
            print(f"Loading repository from local path: {args.local}")
            tool.load_repository(local_path=args.local)
        else:
            print("No repository specified. Using default example repository.")
            tool.load_repository(repo_url="https://github.com/langchain-ai/langchain")

        print("\n=== Codebase Overview ===")
        print(tool.get_codebase_overview())
                
        print("\nYou can now ask questions about the codebase. Type 'exit' to quit.")
        while True:
            question = input("\nQuestion: ")
            if question.lower() == 'exit':
                break
            answer = tool.ask_question(question)
            print(f"\nAnswer: {answer}")        
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if tool.repo_path and os.path.exists(tool.repo_path):
            if args.github:  # Only clean up temp dirs for GitHub clones
                shutil.rmtree(tool.repo_path)

if __name__=="__main__":
    main()