import ast
from typing import List
import yaml


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
        # https://greentreesnakes.readthedocs.io/en/latest/nodes.html?highlight=joinedstr#JoinedStr
        print("JoinedStr not implemented")
        return ""
    elif isinstance(node, ast.Subscript):
        # https://greentreesnakes.readthedocs.io/en/latest/nodes.html?highlight=subscript#Subscript
        print("Subscript not implemented")
        return ""
    elif isinstance(node, ast.Call):
        print("Call not implemented")
        return ""
    elif isinstance(node, ast.BinOp):
        print("BinOp not implemented")
        return ""
    elif isinstance(node, ast.Compare):
        print("Compare not implemented")
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
