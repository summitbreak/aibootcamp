import boto3
from botocore.client import Config
from langchain_aws import ChatBedrock
from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import PromptTemplate
import re
import json

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
Generate a modified version of the source code with upgrades. Modify only the code relevant to the fix.
Provide a response in JSON format with the following keys:
- description: a description of the changes
- title: a title for the upgrade
- source_code: an array of modified file objects with "filename" and "contents" keys

<verion>
{version}
</version>
<code>
{source_code}
</code>
""",
)

class Model:
    """Model class for GenAI."""

    def upgrade_code(self, version, source_code_map):
        """Trigger the code fix generation process."""
        prompt = self._create_prompt(version, source_code_map)
        content = self._invoke(prompt)
        return content
        # cleaned_content = self.clean_result(content)
        # return json.loads(cleaned_content)

    def clean_result(self, content):
        """Clean the response from the model."""
        cleaned_result = content.replace("```", "")
        cleaned_result = remove_newlines(cleaned_result)
        cleaned_result = cleaned_result.strip()
        cleaned_result = cleaned_result.rstrip(",")
        # Replace \n with \\n to escape newlines in JSON
        cleaned_result = cleaned_result.replace("\n", "\\n")
        return cleaned_result

class UpdatedCode(BaseModel):
    filename: str = Field(description="The filename of the modified code")
    code: str = Field(description="The modified code")

class CodeUpgradeResponse(BaseModel):
    code: List[UpdatedCode] = []
    title: str = Field(description="a title for the upgrade")
    description: str = Field(description= "A description of the changes")

class Claude(Model):
    """Claude model class."""

    def __init__(self, model_id=DEFAULT_MODEL, model_aws_region=DEFAULT_MODEL_REGION):
        logger.info(f"Initializing Claude with model_id: {model_id} and region: {model_aws_region}")
        bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=model_aws_region,
            config=config,
        )
        unstructured_llm = ChatBedrock(
            client=bedrock_client,
            region_name = model_aws_region,
            model_id=model_id,
            model_kwargs={
                "temperature": 0.0,
                "max_tokens": 10000,
                # "top_p": 0.999,
                "top_k": 250,
                "stop_sequences": [
                    "\\n\\nHuman::",
                ],
            },
        )
        self.llm = unstructured_llm.with_structured_output(CodeUpgradeResponse)

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

    def _invoke(self, prompt):
        """Invoke the model with the prompt."""
        logger.info(f"Prompt: {prompt}")
        response = self.llm.invoke(prompt)
        # Append opening curly braces which might be missing, depending on the prompt.
        logger.info(f"Raw response from GenAI: {response}")
        # if not response.startswith("{"):
        #     response = "{" + response
        return response

def remove_newlines(json_string):
    """Remove newline characters if they aren't enclosed in double quotes."""
    result = json_string
    result = re.sub('(?<!")\\n', "", result)
    result = re.sub("\\n(?= *})", "", result)
    return result
