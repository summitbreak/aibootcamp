import os
import tempfile
import time
import glob
import json
import asyncio

from git_utils import GitHubProvider, clone_repo, create_branch, update_source_code
from utils import get_logger, get_config
from bedrock import Claude

logger = get_logger()

PARAMETER_NAMES = [
    "ssh_private_key", "api_key"
]
MODEL_AWS_REGION = "us-east-1"

SSH_PRIVATE_KEY_FILENAME = "ssh_private_key"

PARAMETER_STORE_PREFIX = "spring_upgrade_lambda_"# os.environ["PARAMETER_STORE_PREFIX"]
MODEL_AWS_REGION = "us-east-1"

SSH_PRIVATE_KEY_FILENAME = "ssh_private_key"


def api_response(status_code, body):
    """Return a properly formatted API Gateway proxy response."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    """Lambda handler compatible with API Gateway proxy integration.

    Routes:
      GET  /info            - health/info check
      POST /upgrade-project - trigger Spring upgrade
    """
    logger.info(f"Processing event: {event}")

    http_method = event.get("httpMethod", "")
    path = event.get("path", "")

    try:
        if http_method == "GET" and path == "/info":
            return api_response(200, {"status": "ok", "service": "spring-upgrade"})

        elif http_method == "POST" and path == "/upgrade-project":
            body = event.get("body") or "{}"
            if isinstance(body, str):
                body = json.loads(body)

            spring_version = body["spring_version"]
            repo_url = body["github_url"]
            repo_api_url = body["repo_api_url"]

            logger.info(f"Retrieving config")
            config = get_config(PARAMETER_STORE_PREFIX, PARAMETER_NAMES)
            ssh_private_key = config["ssh_private_key"]
            api_key = config["api_key"]

            # Select a model provider to perform the code generation
            provider = Claude(model_aws_region=MODEL_AWS_REGION)

            branch_name = f"upgrade-code-{round(time.time())}"
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            task = loop.create_task(upgrade_code(spring_version, provider, api_key, repo_api_url, repo_url, branch_name, ssh_private_key, context))
            loop.run_until_complete(task)

            return api_response(200, {"branch_name": branch_name})

        else:
            return api_response(404, {"error": f"Route {http_method} {path} not found"})

    except KeyError as e:
        logger.exception(f"Missing required field: {e}")
        return api_response(400, {"error": f"Missing required field: {str(e)}"})
    except json.JSONDecodeError as e:
        logger.exception(f"Invalid JSON body: {e}")
        return api_response(400, {"error": "Invalid JSON body"})
    except Exception as e:
        logger.exception(f"Internal error: {e}")
        return api_response(500, {"error": "Internal server error"})

async def upgrade_code(spring_version, provider, api_key, repo_api_url, repo_url, branch_name, ssh_private_key, context):
    repo_name = repo_url.split("/")[-1]

    # Prepare SSH credentials for cloning the target repo
    tmpdir = tempfile.mkdtemp()
    ssh_private_key_path = os.path.join(tmpdir, "ssh_private_key")
    write_ssh_key(ssh_private_key, ssh_private_key_path)
    
    git_provider = GitHubProvider(api_key, repo_api_url)
    
     # Clone the target repo
    target_repo_dir = os.path.join(tmpdir, context.aws_request_id, repo_name)
    repo = clone_repo(repo_url, target_repo_dir, ssh_private_key_path)


    # Create a map of filenames with the actual filenames in the target repo
    # TODO: optionally include code paths in request
    source_code_map = create_source_code_map(target_repo_dir)

    # Trigger the code generation
    result = provider.upgrade_code(spring_version, source_code_map)

    # Modify the local cloned repo with the generated code
    update_source_code(result.code, target_repo_dir)

    logger.info(f"Updated source code for brance {branch_name}.")

    # Create a branch and commit/push the code to the source repo
    branch_created = create_branch(branch_name, repo, result.description)
    if not branch_created:
        logger.info("No changes were made, exiting.")
        return

    # Create a pull request
    git_provider.create_pull_request(branch_name, result.title, result.description)

    logger.info(f"Created pull request for branch {branch_name}.")


def write_ssh_key(value, file_path):
    """Retrieve git SSH private key from SSM and write to file."""
    logger.info(f"Writing SSH key to {file_path}")
    with open(file_path, "w") as f:
        f.write(value)
    os.chmod(file_path, int("600", base=8))


def find_partial_matches(primary_paths, secondary_paths):
    """Find and return partial matches between file paths in two lists based on filenames.

    This function compares file paths in the `primary_paths` list to those in the `secondary_paths` list
    and returns a list of partial matches if matching filenames are found, regardless of the root directory.

    Example:
        primary_paths = [
            '/var/task/handlers/create_order.py'
        ]
        secondary_paths = [
            '.gitignore',
            'README.md',
            'src',
            'template.yaml',
            'src/handlers',
            'src/requirements.txt',
            'src/handlers/create_order.py',
            'src/handlers/sample.py'
        ]
        results = find_partial_matches(primary_paths, secondary_paths)

    Returns:
        ['src/handlers/sample.py'] if a partial match is found, or an empty list if no matches are found.
    """
    results = []

    for primary_path in primary_paths:
        primary_filename = os.path.basename(primary_path)
        for secondary_path in secondary_paths:
            secondary_filename = os.path.basename(secondary_path)
            if primary_filename == secondary_filename:
                results.append(secondary_path)

    return results


def create_source_code_map(repo_dir):
    """Create a map of relevant filenames with the actual filenames in the target repo."""
    logger.info(f"Creating source code map for {repo_dir}.")
    source_code_map = {}
    pattern = os.path.join(repo_dir, '**/*')
    file_paths_in_repo = glob.glob(pattern, recursive=True)
    for filename in file_paths_in_repo:
        if (os.path.isdir(filename)):
            continue
        with open(os.path.join(repo_dir, filename), "r") as f:
            try:
                source_code_map[filename] = f.read()
            except Exception as e:
                logger.warning(f"Failed parsing file {filename}")
                continue
    return source_code_map


if __name__ == "__main__":

    class MockContext:
        aws_request_id = "1234"

    # Simulate API Gateway proxy event for POST /upgrade-project
    lambda_handler({
        "httpMethod": "POST",
        "path": "/upgrade-project",
        "body": json.dumps({
            "github_url": "https://github.com/summitbreak/aibootcamp",
            "repo_api_url": "https://api.github.com/repos/summitbreak/aibootcamp",
            "spring_version": "Spring boot 2.7"
        })
    },
        MockContext(),
    )
