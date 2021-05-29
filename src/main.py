import json, os
from typing import List, Union
from src.parse_python import socless_lambda_parser
from src.parse_yml import parse_yml
from src.github import (
    get_lambda_folders_data,
    fetch_raw_function,
    fetch_raw_serverless_yml,
)
from src.models import AllIntegrations, IntegrationFamily


def build_socless_info(
    repos: Union[List, str],
    org_name="twilo-labs",
    ghe=False,
    output_file_path="socless_info",
) -> AllIntegrations:
    if isinstance(repos, str):
        repos = repos.split(",")
    repos = [name.strip() for name in repos]

    print(f"fetching socless info for: {repos}")

    all_integrations = AllIntegrations()
    for repo_name in repos:
        integration_family = IntegrationFamily()

        # TODO: make this pull from serverless 'service' name
        integration_family.meta.integration_family = repo_name
        # TODO: create get_repo_url
        # integration_family.meta.repo_url = get_repo_url(repo_name, org_name, ghe=ghe)

        # get serverless.yml function info, names
        raw_yml = fetch_raw_serverless_yml(repo_name, org_name, ghe=ghe)
        all_serverless_fn_meta = parse_yml(raw_yml)

        for folder_data in get_lambda_folders_data(repo_name, org_name, ghe=ghe):
            dir_name = folder_data["name"]
            if dir_name not in all_serverless_fn_meta.functions:
                print(
                    f"File exists for function {dir_name}, but it is not used in serverless.yml. Skip saving info for {dir_name}."
                )
                continue

            raw_function = fetch_raw_function(folder_data, repo_name, org_name, ghe=ghe)
            function_info = socless_lambda_parser(raw_function)

            function_info.meta = all_serverless_fn_meta.functions[dir_name]

            integration_family.functions.append(function_info)
        all_integrations.integrations.append(integration_family)

    if output_file_path and isinstance(output_file_path, str):
        root, ext = os.path.splitext(output_file_path)
        ext = ext if ext else ".json"
        with open(f"{root}{ext}", "w") as f:
            f.write(json.dumps(all_integrations.dict(), indent=4))
    else:
        print(json.dumps(all_integrations.dict()))

    return all_integrations
