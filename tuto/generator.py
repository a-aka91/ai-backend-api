import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

# 1. Load Keys
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 2. Define the Output Structure
# We want the AI to give us specific sections, not just a blob of text.
class ReadmeStructure(BaseModel):
    title: str
    summary: str
    features: list[str]
    usage_instructions: str
    requirements: list[str] # e.g. "Python 3.10", "Node.js"
    complexity_score: int

def generate_readme_data(file_path: Path) -> ReadmeStructure:
    # A. Read the code file
    if not file_path.exists():
        raise FileNotFoundError(f"❌ Could not find file: {file_path}")
    
    source_code = file_path.read_text(encoding="utf-8")
    
    print(f"📖 Reading {file_path.name}...")
    print("🧠 Analyzing code logic...")

    # B. Call OpenAI with Pydantic Parsing
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior technical writer. Analyze the code and generate professional documentation."},
            {"role": "user", "content": f"Here is the source code:\n\n{source_code}"},
        ],
        response_format=ReadmeStructure,
    )

    return completion.choices[0].message.parsed

def save_readme(data: ReadmeStructure, output_path: Path):
    # C. Assemble the Markdown
    # We construct the string manually using the data fields
    markdown_content = f"""# {data.title}
## Summary
{data.summary}

## Key Features
"""
    # Loop through features to make bullet points
    for feature in data.features:
        markdown_content += f"- {feature}\n"

    markdown_content += f"""
## Requirements
{', '.join(data.requirements)}

## Usage
{data.usage_instructions}

## Complexity Score
{data.complexity_score}

"""
    
    # D. Write to disk
    output_path.write_text(markdown_content, encoding="utf-8")
    print(f"✅ Success! Saved to {output_path.name}")

print(f"__name__: {__name__}")
if __name__ == "__main__": 
    # The CLI Loop 
    print("--- Auto-Readme Generator ---")
    user_file = input("Enter the filename to document (e.g., messy_code.js): ")

    path = Path(user_file)
    try:
        # 1. Generate Data
        readme_data = generate_readme_data(path)
        
        # 2. Save File
        output_filename = "README_Generated.md"
        save_readme(readme_data, Path(output_filename))
        
    except Exception as e:
        print(f"Error: {e}")