import os
from requests import get
import time
import json
import fire
import requests
from parsing import socless_lambda_parser, parse_yml
from github import (
    get_lambda_folders_data,
    fetch_raw_function,
    build_serverless_yml_url,
    fetch_raw_serverless_yml,
)

# html_resp = requests.get("https://github.com/twilio-labs/socless-slack")
# https://raw.githubusercontent.com/twilio-labs/socless-slack/master/functions/check_user_in_channel/lambda_function.py

# TODO deprecate this
def build_socless_info(repos, git_url="", write_to_file="socless_info"):
    print(repos)
    if isinstance(repos, str):
        repos = repos.split(",")

    repos = [name.strip() for name in repos]
    socless_info = {}
    for name in repos:
        # get serverless.yml function info, names
        resp = get(build_serverless_yml_url(name))
        resp.raise_for_status()
        yml_info = parse_yml(resp.content)
        time.sleep(1)  # ratelimit prevention
        for raw_lambda_url in get_repo_functions_urls(name):
            # retrive repo info
            # https://raw.githubusercontent.com/twilio-labs/socless-slack/master/functions/check_user_in_channel/lambda_function.py
            split_url = raw_lambda_url.split("/")
            repo_name = split_url[4]
            lambda_dir_name = split_url[7]

            response = get(raw_lambda_url)
            response.raise_for_status()

            if repo_name not in socless_info:
                socless_info[repo_name] = {"functions": {}}

            py_file_info = socless_lambda_parser(response.content)

            # merge yml data with function data in socless_info[repo_name]
            merged_info = {**py_file_info, **yml_info["functions"][lambda_dir_name]}

            socless_info[repo_name]["functions"][lambda_dir_name] = merged_info

            time.sleep(1)  # prevent rate limit for unauthenticated user

    if write_to_file and isinstance(write_to_file, str):
        with open(f"{write_to_file}.json", "w") as f:
            f.write(json.dumps(socless_info))

    return socless_info


def new_build_socless_info(repos, org_name, ghe=False, write_to_file="socless_info"):
    print(f"fetching socless info for: {repos}")
    if isinstance(repos, str):
        repos = repos.split(",")

    repos = [name.strip() for name in repos]

    socless_info = {}
    for repo_name in repos:

        # get serverless.yml function info, names
        raw_yml = fetch_raw_serverless_yml(repo_name, org_name, ghe=ghe)
        yml_info = parse_yml(raw_yml)

        for folder_data in get_lambda_folders_data(repo_name, org_name, ghe=ghe):
            dir_name = folder_data["name"]

            raw_function = fetch_raw_function(folder_data, repo_name, org_name, ghe=ghe)
            py_file_info = socless_lambda_parser(raw_function)

            # merge yml data with function data in socless_info[repo_name]
            merged_info = {**py_file_info, **yml_info["functions"][dir_name]}

            socless_info[repo_name]["functions"][dir_name] = merged_info

    if write_to_file and isinstance(write_to_file, str):
        with open(f"{write_to_file}.json", "w") as f:
            f.write(json.dumps(socless_info))

    return socless_info

    #     for raw_lambda_url in get_repo_functions_urls(name):
    #         # retrive repo info
    #         # https://raw.githubusercontent.com/twilio-labs/socless-slack/master/functions/check_user_in_channel/lambda_function.py
    #         split_url = raw_lambda_url.split("/")
    #         repo_name = split_url[4]
    #         lambda_dir_name = split_url[7]

    #         response = get(raw_lambda_url)
    #         response.raise_for_status()

    #         if repo_name not in socless_info:
    #             socless_info[repo_name] = {"functions": {}}

    #         py_file_info = socless_lambda_parser(response.content)

    #         # merge yml data with function data in socless_info[repo_name]
    #         merged_info = {**py_file_info, **yml_info["functions"][lambda_dir_name]}

    #         socless_info[repo_name]["functions"][lambda_dir_name] = merged_info

    #         time.sleep(1)  # prevent rate limit for unauthenticated user

    # if write_to_file and isinstance(write_to_file, str):
    #     with open(f"{write_to_file}.json", "w") as f:
    #         f.write(json.dumps(socless_info))

    # return socless_info


## test code
# repos = ["socless-slack", "socless"]
# build_socless_info(repos)


import os

if __name__ == "__main__":
    # fire.Fire(build_socless_info)

    domain = os.getenv("GHE_DOMAIN", "api.github.com")
    # url = f"https://{domain}/api/v3/repos/sec-eng/socless-slack" # root
    # url = f"https://{domain}/api/v3/repos/sec-eng/socless-slack/contents/functions?ref=master"  # functions url
    # url = f"https://{domain}/api/v3/repos/sec-eng/socless-slack/contents/functions/check_user_in_channel?ref=master"
    url = f"https://{domain}/api/v3/repos/sec-eng/socless-slack/contents/serverless.yml?ref=master"
    resp = requests.get(
        url, headers={"Authorization": f'token {os.getenv("GHE_TOKEN")}'}
    )

    from pprint import pprint

    # url = resp.json()[0]["download_url"]

    # resp = requests.get(
    #     url, headers={"Authorization": f'token {os.getenv("GHE_TOKEN")}'}
    # )
    print(resp)
    # pprint(resp.content)
    pprint(resp.json())
