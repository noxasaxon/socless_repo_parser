from tree_sitter import Language, Parser


Language.build_library(
    # Store the library in the `build` directory
    "build/my-languages.so",
    # Include one or more languages
    [
        "src/tree_sitter_files",
    ],
)
PY_LANGUAGE = Language("build/my-languages.so", "python")

parser = Parser()
parser.set_language(PY_LANGUAGE)


def test_if_tree_sitter_will_compile():
    import sysconfig
    import _osx_support

    print(sysconfig.get_config_var("CFLAGS"))
    # if this fails, you are not on the right python version
    print(_osx_support._default_sysroot("cc"))


def ts_get_function_name(ts_function_node, source_code_bytes) -> str:
    # fn node.children [0] = "def"
    # fn node.children [1] = <function name>
    fn_name_bytes = source_code_bytes[
        ts_function_node.children[1].start_byte : ts_function_node.children[1].end_byte
    ]
    return fn_name_bytes.decode("UTF-8")


def ts_parse_socless_lambda_file(python_file_as_string):
    source_code_bytes = bytes(python_file_as_string, "utf8")

    tree = parser.parse(source_code_bytes)
    root_node = tree.root_node
    print("root_node")
    # print(tree.root_node)
    # print(dir(tree.root_node))
    # print(tree.root_node.child_by_field_name("handle_state"))
    # print(tree.root_node.children)
    for node in tree.root_node.children:
        if node.type == "function_definition":
            # print(dir(node))
            # print(node.sexp())
            print("FUNCTION NODE")
            fn_name = ts_get_function_name(node, source_code_bytes)
            print(f"Function Name: {fn_name}")
            print(dir(node))
            text = source_code_bytes[node.start_byte : node.end_byte]

            print("next_sibling")
            if node.next_sibling:
                print(node.next_sibling)
                print(
                    source_code_bytes[
                        node.next_sibling.start_byte : node.next_sibling.end_byte
                    ]
                )
            assert False
            # print(
            #     source_code_bytes[
            #         node.next_sibling.start_byte : node.next_sibling.end_byte
            #     ]
            # )

            # for x in node.children:
            #     print(x)

            # print(test)
            print("_______________________")


def test_tree_sitter_parse():
    with open("tests/mock_files/mock_lambda_fn.py") as f:
        python_file_as_string = f.read()

    ts_parse_socless_lambda_file(python_file_as_string)

    assert False
