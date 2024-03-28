import autogen
import os

## Define the function that generates the test case prompt
def get_test_generation_prompt(user_story_text, test_case_component, test_case):
    return f'''
        You are a testing engineer. Write detailed ten test cases for the below specified test case components,

        User story: {user_story_text}
        Test case component: {test_case_component} 
        Test Type: {test_case}

        The test cases should consist of Test ID, Test Name, Test Priority (Low, Medium and High), Test Description, Pre-conditions, Test Data (Relative examples should be provided), Test Steps (along with Navigation steps) and Expected Result, based on the above given components.
    
        Note: The test case should cover all the necessary test cases with 100% test coverage.'''

## Define the configuration for the AssistantAgent
llm_configuration = {
    "config_list": [
        {
            "model": "codellama/CodeLlama-70b-Instruct-hf",
            "api_key": os.environ['TOGETHER_API_KEY'],
            "base_url": "https://api.together.xyz/v1"
        }
    ],
    "cache_seed": 42,
    "temperature": 0.5,
}

## Initialize the AssistantAgent with the provided configuration
assistant = autogen.AssistantAgent(
    name='Test Case Generator',
    llm_config=llm_configuration,
)

## Initialize the UserProxyAgent with the provided configuration
user_proxy = autogen.UserProxyAgent(
    name='user_proxy',
    human_input_mode='TERMINATE',  # # This is for approval and has 3 values: ALWAYS, TERMINATE and NEVER
    llm_config=llm_configuration,
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMTNATE"),  # # Termination message
    code_execution_config={"work_dir": "test_case"},  # # Creates a 'test_case' folder for writing test cases
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
    Otherwise, reply CONTINUE, or the reason why the task is not solved yet.
    """
)

## Define the user story, test component, and test type
user_story = 'As a user of the document preview feature, I want to be able to upload a document and preview it without having to download it first. I also want to have the ability to zoom in and out, view the document in full screen, and see the page numbers. Additionally, I want to have the option to download the uploaded file and extract specific pages or sections from the document.'
test_comp = 'Functionality test cases'
test_type = 'Positive Cases'

## Generate the prompt for test case generation
task = get_test_generation_prompt(user_story, test_comp, test_type)

## Initiate the chat with the assistant to generate test cases
user_proxy.initiate_chat(
    assistant,
    message=task
)
