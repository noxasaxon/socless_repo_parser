from typing import Union
from requests import get
import time
import json
import fire
from parsing import socless_lambda_parser, parse_yml
from github import build_serverless_yml_url, get_repo_functions_urls

# html_resp = requests.get("https://github.com/twilio-labs/socless-slack")
# https://raw.githubusercontent.com/twilio-labs/socless-slack/master/functions/check_user_in_channel/lambda_function.py


def build_socless_info(repos, write_to_file="socless_info"):
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


## test code
# repos = ["socless-slack", "socless"]
# build_socless_info(repos)


if __name__ == "__main__":
    fire.Fire(build_socless_info)
