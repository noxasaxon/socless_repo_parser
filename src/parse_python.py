import ast
from typing import Dict, List
from src.constants import HANDLE_STATE_FN_NAME, INTERNAL_ARG_NAMES
from src.models import SoclessFunction, SoclessFunctionArgument


def convert_python_type_name_to_json_name(py_type_name) -> str:
    if py_type_name == str.__name__:
        return "string"
    elif py_type_name == bool.__name__:
        return "boolean"
    elif py_type_name == int.__name__:
        return "number"
    elif py_type_name == dict.__name__:
        return "object"
    elif py_type_name == list.__name__:
        return "array"
    elif py_type_name == "None":
        return "null"
    else:
        raise NotImplementedError(
            f"No json type conversion configured for python type: {py_type_name}"
        )


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


def get_return_statements(parent_node: ast.FunctionDef):
    return_nodes = parent_return_search(parent_node)

    return_statements = []
    for node in return_nodes:
        if isinstance(node.value, ast.Dict):
            parsed_dict = custom_ast_unpack(node)
            return_statements.append(parsed_dict)
    return return_statements


def get_function_args(node: ast.FunctionDef) -> List[SoclessFunctionArgument]:
    function_args: Dict[str, SoclessFunctionArgument] = {}

    # get all function arguments
    for a in node.args.args:

        arg_info = SoclessFunctionArgument()
        arg_info.name = a.arg
        arg_info.data_type = (
            a.annotation.id if isinstance(a.annotation, ast.Name) else str(a.annotation)
        )
        arg_info.data_type = convert_python_type_name_to_json_name(arg_info.data_type)
        arg_info.description = ""
        arg_info.required = True
        arg_info.placeholder = ""

        if arg_info.name in INTERNAL_ARG_NAMES:
            arg_info.internal = True

        function_args[arg_info.name] = arg_info

    # check if any args have default values
    for name_of_default_arg in node.args.defaults:
        if name_of_default_arg in function_args:
            function_args[name_of_default_arg].required = False

    # TODO: figure out how to parse the docstring effectively for arg descriptions
    # print(ast.get_docstring(node))

    return [x for x in function_args.values()]


def socless_lambda_parser(py_file_string) -> SoclessFunction:
    module = ast.parse(py_file_string)

    try:
        handle_state_node = [
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef) and node.name == HANDLE_STATE_FN_NAME
        ][0]
    except IndexError:
        return SoclessFunction()

    function_info = SoclessFunction()
    function_info.arguments = get_function_args(handle_state_node)
    function_info.return_statements = get_return_statements(handle_state_node)
    function_info.check_and_set_supported_in_playbook()

    # function_info.meta = something
    # function_info.resource_type = something # TODO: figure out how to tell if task or interaction
    # function_info.supported_in_playbook = something # TODO: figure out how to to tell if used in playbooks

    return function_info
