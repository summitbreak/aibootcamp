import boto3
from botocore.client import Config
from langchain_aws import ChatBedrock
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from typing import List
from langchain_core.prompts import PromptTemplate
# from langchain_community.agent_toolkits import FileManagementToolkits
import re
import json
import subprocess
import sys

from utils import get_logger

config = Config(connect_timeout=240, read_timeout=240)


logger = get_logger()

DEFAULT_MODEL = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
DEFAULT_MODEL_REGION = "us-east-1"
PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["version", "source_code"],
    template="""
Human: 
You are a code upgrading assistant for Spring and Spring boot.
You will upgrade the provided source code to the given Spring version.
Generate a modified version of the source code with upgrades. Modify only the code relevant to the upgrade.

<verion>
{version}
</version>
<code>
{source_code}
</code>
""",
)

TEST_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["code_dir"],
    template="""
Human: 
Please execute unit tests on {code_dir} using mvn test and  tell me how many tests failed.
You should also include recommendations on fixing test failures. if there are any.

<code_directory>
{code_dir}
</code_directory
""",
)

class Model:
    """Model class for GenAI."""

    def upgrade_code(self, version, source_code_map):
        """Trigger the code fix generation process."""
        prompt = self._create_prompt(version, source_code_map)
        content = self._invoke(prompt)
        return content
    
    def test_code(self, code_dir):
        # run_maven_test2(code_dir)
        # file_tools = FileManagementToolkit(root_dir=str(code_dir)).get_tools()
        prompt = self._create_test_prompt(code_dir)

        content = self.test_llm.invoke({"messages": [{"role": "user", "content": prompt}]})
        print(content)
        return content

class UpdatedCode(BaseModel):
    filename: str = Field(description="The filename of the modified code")
    code: str = Field(description="The modified code")

class CodeUpgradeResponse(BaseModel):
    code: List[UpdatedCode] = []
    title: str = Field(description="A title for the upgrade")
    description: str = Field(description= "A description of the changes")


class Claude(Model):
    """Claude model class."""

    def __init__(self, model_id=DEFAULT_MODEL, model_aws_region=DEFAULT_MODEL_REGION):
        logger.info(f"Initializing Claude with model_id: {model_id} and region: {model_aws_region}")
        bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=model_aws_region,
            config=config
        )

        # Create agent with tools
        unstructured_llm = ChatBedrock(
            client=bedrock_client,
            region_name = model_aws_region,
            model_id=model_id,
            model_kwargs={
                "temperature": 0.0,
                "max_tokens": 10000,
                # "top_p": 0.999,
                # "top_k": 250,
                "stop_sequences": [
                    "\\n\\nHuman::",
                ],
            },
        )

        self.llm = unstructured_llm.with_structured_output(CodeUpgradeResponse)
        test_llm = unstructured_llm.bind_tools([run_maven_test])
        self.test_llm = create_agent(test_llm, [run_maven_test])
        logger.info("Initialized Claude")

    def _create_prompt(self, version, source_code_map):
        """Create a prompt for the model to generate a code upgrade."""
        logger.info("Creating prompt for model")
        source_code_parts = []
        for filename, source_code in source_code_map.items():
            source_code_parts.append(
                f"File: {filename}\n\nContents:\n{source_code}\n\n"
            )
        concatenated_source_code = "\n".join(source_code_parts)
        prompt = PROMPT_TEMPLATE.format(
            version=version, source_code=concatenated_source_code
        )
        return prompt
    def _create_test_prompt(self, code_dir):
        """Create a prompt for the model to generate a code upgrade."""
        logger.info("Creating test prompt for model")   
        prompt = TEST_PROMPT_TEMPLATE.format(code_dir=code_dir)
        return prompt

    def _invoke(self, prompt):
        """Invoke the model with the prompt."""
        response = self.llm.invoke(prompt)
        # Append opening curly braces which might be missing, depending on the prompt.
        logger.info(f"Raw response from GenAI: {response}")
        # if not response.startswith("{"):
        #     response = "{" + response
        return response
    
    def _invoke_unstructured(self, prompt):
        """Invoke the model with the prompt."""
        response = self.unstructured_llm.invoke(prompt)
        logger.info(f"Raw response from GenAI: {response}")
        return response

def remove_newlines(json_string):
    """Remove newline characters if they aren't enclosed in double quotes."""
    result = json_string
    result = re.sub('(?<!")\\n', "", result)
    result = re.sub("\\n(?= *})", "", result)
    return result

@tool
def run_maven_test(code_dir: str) -> str:
    """Runs a shell command using subprocess and handles potential errors.

    Args:
        code_dir: The code directory to execute unit tests from.
    """
    logger.info(f"Running maven tests in directory: {code_dir}")
    print(f"Running: mvn test -f {code_dir}")
    command = f'mvn test -f {code_dir}'
    try:
        # Capture the output and check the return code
        result = subprocess.run(command, check=True, shell=True, capture_output=True, text=True)
        print(result)
        return result.stdout if result.returncode == 0 else result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with return code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return e.stderr
    