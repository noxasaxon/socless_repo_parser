from src.main import build_socless_info


def test_build_socless_info_with_comma_separated_string():
    info = build_socless_info(
        "socless, socless-slack",
        org_name="twilio-labs",
        output_file_path="socless_info.json",
    )

    assert isinstance(info, dict)
