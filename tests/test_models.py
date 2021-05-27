from src.models import IntegrationFamily, build_integration_classes_from_json
from pydantic.json import pydantic_encoder
import json

mock_json_output = {
    "socless-slack": {
        "meta": {
            "repo_url": "https://www.github.com/twilio-labs/socless-slack",
            "integration_family": "socless-slack",
        },
        "functions": {
            "check_user_in_channel": {
                "meta": {
                    "lambda_folder_name": "check_user_in_channel",
                    "deployed_lambda_name": "socless_slack_check_user_in_channel",
                    "serverless_lambda_name": "CheckIfUserInChannel",
                    "supported_in_playbook": True,
                },
                "resource_type": "socless_task",
                "arguments": {
                    "user_id": {
                        "name": "user_id",
                        "data_type": "string",
                        "required": True,
                        "description": "",
                        "placeholder": "",
                    },
                    "target_channel_id": {
                        "name": "target_channel_id",
                        "data_type": "string",
                        "required": True,
                        "description": "",
                        "placeholder": "",
                    },
                },
                "return_statements": [{"ok": True}, {"ok": False}],
            },
        },
    }
}


# def test_generate_jsonschema():
#     test = IntegrationFamily().__pydantic_model__.schema_json()
#     print(test)
#     assert test
#     raise AssertionError()


def test_generate_dataclasses_from_json():
    output = build_integration_classes_from_json(mock_json_output)
    assert json.dumps(output["socless-slack"], default=pydantic_encoder) == json.dumps(
        mock_json_output["socless-slack"]
    )
