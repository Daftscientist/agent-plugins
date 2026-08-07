import pytest
from pydantic import ValidationError

from office_mcp.ids import element_id, presentation_id, revision_id, slide_id
from office_mcp.models.common import CustomSlideSize, SlideTransition
from office_mcp.models.element import AttributeMutation, ElementMutation, StyleMutation
from office_mcp.models.presentation import PresentationCreateArgs, PresentationUpdateArgs
from office_mcp.models.preview import PreviewRange
from office_mcp.models.slide import SlideDeleteArgs, SlideUpdateArgs


def test_opaque_ids_match_public_prefixes() -> None:
    assert presentation_id().startswith("prs_")
    assert revision_id().startswith("rev_")
    assert slide_id().startswith("sld_")
    assert element_id().startswith("el_")
    assert len({presentation_id() for _ in range(100)}) == 100


def test_strict_models_reject_unknown_fields_and_coercion() -> None:
    with pytest.raises(ValidationError):
        PresentationCreateArgs.model_validate({"name": "x", "unknown": True})
    with pytest.raises(ValidationError):
        PresentationCreateArgs.model_validate({"name": 12})


def test_slide_size_and_transition_enums_are_closed() -> None:
    assert CustomSlideSize(width_in=56, height_in=1).width_in == 56
    assert SlideTransition.MORPH == "morph"
    with pytest.raises(ValidationError):
        CustomSlideSize(width_in=56.01, height_in=1)


def test_patch_models_track_omission_and_explicit_null() -> None:
    patch = PresentationUpdateArgs(presentation_id=presentation_id(), description=None)
    assert patch.model_fields_set >= {"presentation_id", "description"}
    with pytest.raises(ValidationError):
        PresentationUpdateArgs(presentation_id=presentation_id())
    with pytest.raises(ValidationError):
        SlideUpdateArgs(presentation_id=presentation_id(), slide_id=slide_id())


def test_element_mutation_contracts() -> None:
    with pytest.raises(ValidationError):
        ElementMutation.model_validate(
            {
                "element": {"type": "id", "element_id": element_id()},
                "text": "a",
                "inner_html": "<b>b</b>",
            }
        )
    with pytest.raises(ValidationError):
        StyleMutation(set={"color": "red"}, remove=["COLOR"])
    with pytest.raises(ValidationError):
        AttributeMutation(set={"data-office-id": element_id()})
    with pytest.raises(ValidationError):
        AttributeMutation(set={"onclick": "bad()"})


def test_range_and_duplicate_slide_ids_are_rejected() -> None:
    with pytest.raises(ValidationError):
        PreviewRange(start=3, end=2)
    identifier = slide_id()
    with pytest.raises(ValidationError):
        SlideDeleteArgs(presentation_id=presentation_id(), slide_ids=[identifier, identifier])


def test_generated_schemas_include_bounds_discriminators_and_forbid_extra() -> None:
    schema = PresentationCreateArgs.model_json_schema()
    assert schema["additionalProperties"] is False
    assert schema["properties"]["name"]["minLength"] == 1
    assert schema["properties"]["slides"]["maxItems"] == 100
    size = schema["properties"]["size"]
    assert size["discriminator"]["propertyName"] == "type"
