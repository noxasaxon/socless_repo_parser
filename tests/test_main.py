from src.models import build_integration_classes_from_json
from src.main import build_socless_info


def test_output_structure():
    output = build_socless_info(
        "socless, socless-slack",
        org_name="twilio-labs",
        output_file_path="socless_info.json",
    )

    back_to_classes = build_integration_classes_from_json(output.dict())
    assert len(back_to_classes.integrations) > 0
