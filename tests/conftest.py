import json
import pytest


@pytest.fixture(scope="session")
def mock_socless_info_output_as_json() -> dict:
    # output generated by running `python3 main.py "socless, socless-slack" --org-name="twilio-labs"` on 7/19/2021
    with open("tests/mock_files/mock_output.json") as f:
        mock_output = json.loads(f.read())
    return mock_output
