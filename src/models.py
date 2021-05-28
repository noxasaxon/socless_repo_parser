# from pydantic import Field
import json
from dataclasses import field, asdict
from pydantic.dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Union


class SoclessFunctionMeta(BaseModel):
    lambda_folder_name: str  # check_user_in_channel,
    deployed_lambda_name: str  # socless_slack_check_user_in_channel,
    serverless_lambda_name: str  # CheckIfUserInChannel,
    supported_in_playbook: bool


class SoclessResourceType(str, Enum):
    socless_task = "socless_task"
    socless_interaction = "socless_interaction"


class SoclessFunctionArgument(BaseModel):
    name: str
    data_type: str
    required: bool
    description: str
    placeholder: str


class SoclessFunction(BaseModel):
    meta: SoclessFunctionMeta
    resource_type: SoclessResourceType
    arguments: List[SoclessFunctionArgument] = Field(default_factory=lambda: [])
    return_statements: List[Dict[str, Any]] = Field(default_factory=lambda: [])


class IntegrationMeta(BaseModel):
    repo_url: str = ""
    integration_family: str = ""


class IntegrationFamily(BaseModel):
    meta: IntegrationMeta
    functions: List[SoclessFunction] = Field(default_factory=lambda: [])


class AllIntegrations(BaseModel):
    integrations: List[IntegrationFamily] = Field(default_factory=[])


def build_integration_classes_from_json(input: Union[str, dict]) -> AllIntegrations:
    if isinstance(input, str):
        input = json.loads(input)

    all_integrations = []

    for integration_family in input["integrations"]:
        all_integrations.append(IntegrationFamily(**integration_family))

    output = AllIntegrations(integrations=all_integrations)

    return output
