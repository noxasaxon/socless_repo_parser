import json, os
from typing import List, Union
from src.parsing import socless_lambda_parser, parse_yml
from src.github import (
    get_lambda_folders_data,
    fetch_raw_function,
    fetch_raw_serverless_yml,
)
from src.models import IntegrationFamily


def build_socless_info(
    repos: Union[List, str],
    org_name="twilo-labs",
    ghe=False,
    output_file_path="socless_info",
):
    """Fetch and parse SOCless repos' raw files from github, formatting data into single json object.
    Args:
        repos: "socless, socless-slack" | ["socless", "socless-slack"]
        org_name: your github organization or profile name
        ghe: bool - if using Github Enterprise, set GHE_DOMAIN and GHE_TOKEN environment vars
        output_file_path: str - filename for json output. if empty, will print to stdout instead

    For Github Enterprise:
    ```
        export GHE_DOMAIN=<Your_GHE_Domain.com>
        export GHE_TOKEN=<Personal_Access_Token>
        python3 main.py "socless-slack, socless" --org_name=<Org_Name> --ghe=True
    ```
    """
    if isinstance(repos, str):
        repos = repos.split(",")
    repos = [name.strip() for name in repos]

    print(f"fetching socless info for: {repos}")

    socless_info = {}
    for repo_name in repos:
        socless_info[repo_name] = {"functions": {}}

        # get serverless.yml function info, names
        raw_yml = fetch_raw_serverless_yml(repo_name, org_name, ghe=ghe)
        yml_info = parse_yml(raw_yml)

        for folder_data in get_lambda_folders_data(repo_name, org_name, ghe=ghe):
            dir_name = folder_data["name"]
            if dir_name not in yml_info["functions"]:
                print(
                    f"File exists for function {dir_name}, but it is not used in serverless.yml. Skip saving info for {dir_name}."
                )
                continue

            raw_function = fetch_raw_function(folder_data, repo_name, org_name, ghe=ghe)
            py_file_info = socless_lambda_parser(raw_function)

            # merge yml data with function data in socless_info[repo_name]

            merged_info = {**py_file_info, **yml_info["functions"][dir_name]}

            socless_info[repo_name]["functions"][dir_name] = merged_info

    if output_file_path and isinstance(output_file_path, str):
        root, ext = os.path.splitext(output_file_path)
        ext = ext if ext else ".json"
        with open(f"{root}{ext}", "w") as f:
            f.write(json.dumps(socless_info, indent=4))
    else:
        print(json.dumps(socless_info))

    return socless_info
