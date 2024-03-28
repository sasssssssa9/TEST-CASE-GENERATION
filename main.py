from fastapi import FastAPI, HTTPException, Depends, Response
from pydantic import BaseModel
from openai import OpenAI
import csv
from typing import List
import re

app = FastAPI()

TOGETHER_API_KEY = "793baad9e1dbe34e5f99374a910b9605ecd353a8016f90a5cb0582b4c0a0d6da"
TOGETHER_MODEL = "codellama/CodeLlama-70b-Instruct-hf"
together_client = OpenAI(api_key=TOGETHER_API_KEY, base_url="https://api.together.xyz")

class TestcaseGeneration(BaseModel):
    user_story: str
    components: str
    test_case_types: List[str]
    prompt: str = None
    system_prompt: str = None
    max_tokens: int = None

def extract_test_cases_from_string(test_cases_string):
    # Define the regular expression pattern to match each test case
    test_case_pattern = r"\d+\.\s+Test\s+ID:\s+(.?)\n\s+Test\s+Data:\s+(.?)\n\s+Test\s+Description:\s+(.?)\n\s+Expected\s+Output:\s+(.?)\n"
    
    # Find all matches of the pattern in the test_cases_string
    matches = re.findall(test_case_pattern, test_cases_string, re.DOTALL)

    extracted_test_cases = []
    for match in matches:
        test_id, test_data, description, expected_output = match
        extracted_test_cases.append({
            "Test ID": test_id.strip(),
            "Test Data": test_data.strip(),
            "Test Description": description.strip(),
            "Expected Output": expected_output.strip()
        })

    return extracted_test_cases

def generate_test_cases_csv(test_cases_string):
    # Extract test cases from the response string
    extracted_test_cases = extract_test_cases_from_string(test_cases_string)

    # Write extracted test cases to CSV string
    csv_string = "Test ID,Test Data,Test Description,Expected Output\n"
    for test_case in extracted_test_cases:
        csv_string += ','.join(test_case.values()) + '\n'

    return csv_string

@app.post("/generate-test-cases/")
async def get_test_cases(request_data: TestcaseGeneration = Depends()):
    # Generate test cases using OpenAI
    prompt = f"""
    You are a testing engineer. Please write ten test cases following the format:
    Test ID:
    Test Data:
    Test Description:
    Expected Output:
    * Based on the following details:
    User Story:
    {request_data.user_story}
    Components:
    {request_data.components}
    Test Case Types:
    {', '.join(request_data.test_case_types)}
    Your Prompt:
    {request_data.prompt}
    """

    chat_completion = together_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=TOGETHER_MODEL,
        max_tokens=request_data.max_tokens or 1024,
        temperature=0.5,
    )

    response_json = chat_completion.choices[0].message.content
    
    # Generate CSV string from the response JSON
    test_cases_csv_data = generate_test_cases_csv(response_json)

    # Return CSV response
    return Response(content=test_cases_csv_data, media_type="text/csv")