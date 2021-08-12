# from pydantic import Field
import json
from enum import Enum
from pydantic import BaseModel
from typing import Dict, List, Any, Optional, Union
from src.constants import INTERACTION_ARG_NAMES
from github.Repository import Repository
from github.ContentFile import ContentFile
from dataclasses import dataclass


@dataclass
class RepoNameInfo:
    name: str
    org: str


@dataclass
class FileExistence:
    gh_repo: Repository
    file_path: str
    branch_exists: bool = False
    file_exists: bool = False
    file_contents: Union[bool, ContentFile, List[ContentFile]] = False


class SoclessFunctionMeta(BaseModel):
    lambda_folder_name: str = ""  # check_user_in_channel,
    deployed_lambda_name: str = ""  # socless_slack_check_user_in_channel,
    serverless_lambda_name: str = ""  # CheckIfUserInChannel
    supported_in_playbook: bool = True


# class SliceType(BaseModel):
#     type_name: str
#     items: List[str]

#     def __repr__(self) -> str:
#         items_as_string = ""
#         for i, item in enumerate(self.items):
#             if i == 0:
#                 items_as_string += f"{item}"
#             else:
#                 items_as_string += f",{item}"
#         return f"{self.type_name}<{items_as_string}>"

#     def __eq__(self, o: object) -> bool:
#         return str(self) == str(o)


# class ArrayType(SliceType):
#     type_name: str = "array"
#     items: List[Union[str, SliceType]]


# class UnionType(SliceType):
#     type_name = "union"
#     items: List[Union[str, ArrayType]]


class JsonDataType(str, Enum):
    STRING = "string"
    BOOLEAN = "boolean"
    NUMBER = "number"
    OBJECT = "object"
    NULL = "null"
    ARRAY = "array<>"
    UNION = "union<>"
    ANY = "any"


class SoclessFunctionArgument(BaseModel):
    """
    data_type: "string"|"number"|"boolean"|"object"|"array<>"|"array<data_type>"|"null"
        If a type hint or default value is specified, what (JSON) data type is it.
    required: # Does this argument have a default value.
    description: # TODO: Not yet implemented.
    placeholder: # TODO: Not fully implemented, but `placeholder` is currently populated with
            the default_value (if default_value is not empty)
    internal: # Custom field for marking args not used in `playbook.json`, such as `context`. TODO: Needs better logic
    default_value: # The default value for a given arg (if provided.) Ex: def myfn(my_arg: str = "a default")"""

    name: str = ""
    data_type: Union[JsonDataType, str] = JsonDataType.NULL
    required: bool = False
    description: str = ""
    placeholder: Any = ""
    internal: bool = False
    default_value: Optional[Any]


class SoclessResourceType(str, Enum):
    SOCLESS_TASK = "socless_task"
    SOCLESS_INTERACTION = "socless_interaction"


class SoclessFunction(BaseModel):
    meta: SoclessFunctionMeta = SoclessFunctionMeta()
    resource_type: SoclessResourceType = SoclessResourceType.SOCLESS_TASK
    arguments: List[SoclessFunctionArgument] = []
    supports_kwargs: bool = False
    return_statements: List[Dict[str, Any]] = []

    def check_and_set_supported_in_playbook(self):
        for arg in self.arguments:
            if arg.name in INTERACTION_ARG_NAMES:
                self.resource_type = SoclessResourceType.SOCLESS_INTERACTION


class IntegrationMeta(BaseModel):
    repo_url: str = ""
    integration_family: str = ""


class IntegrationFamily(BaseModel):
    meta: IntegrationMeta = IntegrationMeta()
    functions: List[SoclessFunction] = []


class AllIntegrations(BaseModel):
    integrations: List[IntegrationFamily] = []


def build_integration_classes_from_json(input: Union[str, dict]) -> AllIntegrations:
    if isinstance(input, str):
        input = json.loads(input)

    all_integrations = []

    for integration_family in input["integrations"]:
        all_integrations.append(IntegrationFamily(**integration_family))

    output = AllIntegrations(integrations=all_integrations)

    return output
