import ast
from src.models import SoclessFunction, SoclessFunctionArgument
from src.parse_python import (
    get_function_args_info,
    socless_lambda_parser,
)


def mock_handle_state_function() -> ast.FunctionDef:
    mock_handle_state_fn_def = """
def tester(no_type_info_test, str_test: str, list_test: list, dict_test: dict, int_test: int, none_test = None, empty_dict_test = {}, union_test: Union[str, list] = [], optional_test: Optional[str] = "", list_typing_test: List[str] = [], **kwargs):
    pass
    """
    mock_ast_module = ast.parse(mock_handle_state_fn_def)
    for node in mock_ast_module.body:
        if isinstance(node, ast.FunctionDef):
            return node
    raise NotImplementedError("No function definition in mock ast data")


def expected_parsed_fn_for_mock_handle_state() -> SoclessFunction:
    mock_function = SoclessFunction()
    mock_function.arguments = [
        SoclessFunctionArgument(
            name="no_type_info_test",
            data_type="null",
            required=True,
            description="",
            placeholder="",
            internal=False,
            default_value=None,
        ),
        SoclessFunctionArgument(
            name="str_test",
            data_type="string",
            required=True,
            description="",
            placeholder="",
            internal=False,
            default_value=None,
        ),
        SoclessFunctionArgument(
            name="list_test",
            data_type="array<>",
            required=True,
            description="",
            placeholder="",
            internal=False,
            default_value=None,
        ),
        SoclessFunctionArgument(
            name="dict_test",
            data_type="object",
            required=True,
            description="",
            placeholder="",
            internal=False,
            default_value=None,
        ),
        SoclessFunctionArgument(
            name="int_test",
            data_type="number",
            required=True,
            description="",
            placeholder="",
            internal=False,
            default_value=None,
        ),
        SoclessFunctionArgument(
            name="none_test",
            data_type="null",
            required=False,
            description="",
            placeholder="",
            internal=False,
            default_value=None,
        ),
        SoclessFunctionArgument(
            name="empty_dict_test",
            data_type="object",
            required=False,
            description="",
            placeholder="",
            internal=False,
            default_value={},
        ),
        SoclessFunctionArgument(
            name="union_test",
            data_type="union<string,array<>>",
            required=False,
            description="",
            placeholder="",
            internal=False,
            default_value=[],
        ),
        SoclessFunctionArgument(
            name="optional_test",
            data_type="string",
            required=False,
            description="",
            placeholder="",
            internal=False,
            default_value="",
        ),
        SoclessFunctionArgument(
            name="list_typing_test",
            data_type="array<string>",
            required=False,
            description="",
            placeholder="",
            internal=False,
            default_value=[],
        ),
    ]
    return mock_function


def test_fn_args_parse():
    function_info = SoclessFunction()
    function_info.arguments = get_function_args_info(mock_handle_state_function())
    expected_fn = expected_parsed_fn_for_mock_handle_state()
    assert function_info.arguments == expected_fn.arguments


def test_socless_lambda_parser():
    with open("tests/mock_files/mock_lambda_fn.py") as f:
        python_file_as_string = f.read()
    _ = socless_lambda_parser(python_file_as_string)
