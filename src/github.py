import requests


def build_raw_lambda_url(
    repo_name,
    lambda_folder_name,
    org_name="twilio-labs",
    lambda_file_name="lambda_function.py",
    branch="master",
):
    return f"https://raw.githubusercontent.com/{org_name}/{repo_name}/{branch}/functions/{lambda_folder_name}/{lambda_file_name}"


def get_repo_functions_urls(repo_name, org_name="twilio-labs"):
    functions_folder_url = f"https://api.github.com/repos/{org_name}/{repo_name}/contents/functions?ref=master"

    api_resp = requests.get(functions_folder_url)
    api_resp.raise_for_status()
    api_resp = api_resp.json()

    python_file_urls = []

    for item in api_resp:
        if item["type"] == "dir":
            file_url = build_raw_lambda_url(repo_name, item["name"])
            python_file_urls.append(file_url)

    return python_file_urls


def build_serverless_yml_url(
    repo_name,
    org_name="twilio-labs",
    lambda_file_name="lambda_function.py",
    branch="master",
):
    return f"https://raw.githubusercontent.com/{org_name}/{repo_name}/{branch}/serverless.yml"
