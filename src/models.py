# from pydantic import Field
# from dataclasses import field, asdict
from pydantic.dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class SoclessFunctionMeta:
    lambda_folder_name: str  # check_user_in_channel,
    deployed_lambda_name: str  # socless_slack_check_user_in_channel,
    serverless_lambda_name: str  # CheckIfUserInChannel,
    supported_in_playbook: bool


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
    resource_type: str  # socless_task | socless_interaction
    arguments: Dict[str, SoclessFunctionArgument]
    return_statements: List[Any]


@dataclass
class IntegrationMeta:
    repo_url: str
    integration_family: str


@dataclass
class IntegrationFamily:
    meta: IntegrationMeta
    functions: List[SoclessFunction]
