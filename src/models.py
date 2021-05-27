# from pydantic import Field
import json
from dataclasses import field, asdict
from pydantic.dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Union


@dataclass
class SoclessFunctionMeta:
    lambda_folder_name: str  # check_user_in_channel,
    deployed_lambda_name: str  # socless_slack_check_user_in_channel,
    serverless_lambda_name: str  # CheckIfUserInChannel,
    supported_in_playbook: bool


class SoclessResourceType(str, Enum):
    socless_task = "socless_task"
    socless_interaction = "socless_interaction"


@dataclass
class SoclessFunctionArgument:
    name: str
    data_type: str
    required: bool
    description: str
    placeholder: str


@dataclass
class SoclessFunction:
    meta: SoclessFunctionMeta
    resource_type: SoclessResourceType
    arguments: Dict[str, SoclessFunctionArgument] = field(default_factory=lambda: {})
    return_statements: List[Dict[str, Any]] = field(default_factory=lambda: [])


@dataclass
class IntegrationMeta:
    repo_url: str = ""
    integration_family: str = ""


@dataclass
class IntegrationFamily:
    meta: IntegrationMeta
    functions: Dict[str, SoclessFunction] = field(default_factory=lambda: {})


def build_integration_classes_from_json(
    input: Union[str, dict]
) -> Dict[str, IntegrationFamily]:
    if isinstance(input, str):
        input = json.loads(input)

    output = {}

    for family_name, integration_family in input.items():
        output[family_name] = IntegrationFamily(**integration_family)

    return output
