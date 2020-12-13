import ast
from typing import List
import requests
from requests import get
from pprint import pprint
import time
import json
import yaml
import fire


#! ##### parsing.py
def parent_return_search(parent_node: ast.FunctionDef) -> List[ast.Return]:
    """Look for return statements in an ast FunctionDef"""
    parent_return_nodes: list[ast.Return] = []

    def recursive_search(node: ast.AST):
        for child_node in ast.iter_child_nodes(node):
            if isinstance(child_node, ast.FunctionDef):
                print(
                    f"child function node found ({child_node.name}), don't look for Return'"
                )
                return
            elif isinstance(child_node, ast.Return):
                parent_return_nodes.append(child_node)
            else:
                recursive_search(child_node)

    recursive_search(parent_node)
    return parent_return_nodes


def get_function_args(node: ast.FunctionDef) -> dict:
    function_args = {}

    # get all function arguments
    for a in node.args.args:
        arg_name = a.arg
        function_args[arg_name] = {
            "name": arg_name,
            "required": True,
            "description": "",
        }

    # check if any args have default values
    for default in node.args.defaults:
        if default in function_args:
            function_args[default]["required"] = False

    # TODO: figure out how to parse the docstring effectively for arg descriptions
    # print(ast.get_docstring(node))

    return function_args


def custom_ast_unpack(node):
    try:
        parsed = ast.literal_eval(node)
        return parsed
    except Exception:
        pass

    if isinstance(node, ast.NameConstant):
        return node.value
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.JoinedStr):
        print("JoinedStr not implemented")
        return ""
    elif isinstance(node, ast.Return):
        return custom_ast_unpack(node.value)
    elif isinstance(node, ast.Attribute):
        return custom_ast_unpack(node.value)
    elif isinstance(node, ast.Dict):
        parsed_dict = {}
        tuples_kv = zip(node.keys, node.values)
        for k, v in tuples_kv:
            key = custom_ast_unpack(k)
            parsed_dict[key] = custom_ast_unpack(v)
        return parsed_dict
    else:
        raise Exception(f"Not yet implemented for {node} ")


def socless_lambda_parser(py_file_string):
    module = ast.parse(py_file_string)

    function_nodes = [
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "handle_state"
    ]
    if not function_nodes:
        return {}
    handle_state_node = function_nodes[0]

    function_args = get_function_args(handle_state_node)

    return_nodes = parent_return_search(handle_state_node)
    return_statements = []
    for node in return_nodes:
        if isinstance(node.value, ast.Dict):
            parsed_dict = custom_ast_unpack(node)
            return_statements.append(parsed_dict)

    socless_function_info = {
        "arguments": function_args,
        "return_statements": return_statements,
    }

    return socless_function_info


#! #### github.py

# html_resp = requests.get("https://github.com/twilio-labs/socless-slack")
# https://raw.githubusercontent.com/twilio-labs/socless-slack/master/functions/check_user_in_channel/lambda_function.py


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


def parse_yml(raw_yml):
    yml_dict = yaml.safe_load(raw_yml)
    yml_functions = yml_dict["functions"]

    lambda_functions = {}

    for sls_lambda_name, func_obj in yml_functions.items():

        lambda_folder_name = func_obj["package"]["include"][0].split("/")[1]

        deployed_lambda_name = func_obj["name"]

        lambda_functions[lambda_folder_name] = {
            "lambda_folder_name": lambda_folder_name,
            "deployed_lambda_name": deployed_lambda_name,
            "serverless_lambda_name": sls_lambda_name,
        }

    # nothing else needed from serverless.yml right now
    return {"functions": lambda_functions}


def parse_serverless_yaml(repo):
    """Pull SOCless info out of serverless.yml
    MVP:
        get function folder names and deployed function names
    Stretch Goals:
        reliably find SSM info
    """
    repo_info = {}
    try:
        with open(f"{repo.cache_path}/serverless.yml", "r") as serverless_stream:
            yaml_dict = yaml.safe_load(serverless_stream)

            # get function info
            repo_info["functions"] = {}
            for output_name, func in yaml_dict["functions"].items():
                repo_info["functions"][output_name] = {
                    "output_name": output_name,
                    "description": func["description"] if "description" in func else "",
                    "file_name": func["name"],
                    "file_location": func["package"]["include"][0],
                }
    except FileNotFoundError:
        # repo doesnt have a serverless.yml (doesn't deploy i.e. socless_python)
        return repo_info

    return repo_info


######################
######################

repos = ["socless-slack", "socless"]


# for repo in repos:
#   get_repo_functions_urls(repo)
def build_socless_info(repo_names, write_to_file="socless_info"):
    socless_info = {}
    for name in repo_names:
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


build_socless_info(repos)
