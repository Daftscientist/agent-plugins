import pytest
from bs4 import BeautifulSoup

from office_mcp.domain.html import parse_styles, sanitize_fragment, select_element
from office_mcp.errors import ErrorCode, OfficeError
from office_mcp.models.element import ElementByName


@pytest.mark.parametrize(
    "html",
    [
        "<script>alert(1)</script>",
        "<iframe src='https://example.com'></iframe>",
        "<style>p{color:red}</style><p>x</p>",
        "<p onclick='bad()'>x</p>",
        "<a href='javascript:bad()'>x</a>",
        "<link rel='preload' href='https://example.com/x'>",
        "<img src='https://example.com/x.png'>",
        "<img srcset='https://example.com/x.png 1x'>",
        '<div style="background-image:u\\72l(https://example.com/x.png)">x</div>',
    ],
)
def test_active_html_is_rejected(html: str) -> None:
    with pytest.raises(OfficeError) as error:
        sanitize_fragment(html)
    assert error.value.code is ErrorCode.UNSAFE_HTML


def test_server_replaces_spoofed_ids_and_strips_classes() -> None:
    result, assigned = sanitize_fragment(
        '<section data-office-id="el_attacker" class="styled"><h1>x</h1></section>'
    )
    assert "el_attacker" not in result
    assert "class=" not in result
    assert len(assigned) == 2
    assert all(identifier in result for identifier in assigned)


def test_inline_style_is_normalized_and_unsafe_css_url_rejected() -> None:
    assert parse_styles("COLOR: red; font-size: 20px") == {"color": "red", "font-size": "20px"}
    with pytest.raises(OfficeError):
        parse_styles("background-image:url(http://127.0.0.1/x)")


def test_ambiguous_semantic_name_never_guesses() -> None:
    html, _ = sanitize_fragment(
        '<section><p data-office-name="metric">1</p><p data-office-name="metric">2</p></section>'
    )
    with pytest.raises(OfficeError) as error:
        select_element(BeautifulSoup(html, "html.parser"), ElementByName(element_name="metric"))
    assert error.value.code is ErrorCode.AMBIGUOUS_ELEMENT_NAME


def test_exactly_one_root_is_enforced() -> None:
    with pytest.raises(OfficeError):
        sanitize_fragment("<p>a</p><p>b</p>", exactly_one_root=True)


def test_only_closed_document_assets_and_safe_links_are_allowed() -> None:
    result, _ = sanitize_fragment(
        '<section><img src="data:image/png;base64,iVBORw0KGgo=">'
        '<a href="https://example.com/docs">docs</a><a href="#local">local</a></section>'
    )
    assert "data:image/png" in result and "https://example.com/docs" in result


def test_internal_id_preservation_is_private_strict_and_unique() -> None:
    original, assigned = sanitize_fragment("<section><p>x</p></section>")
    preserved, new_ids = sanitize_fragment(original, _preserve_office_ids=True)
    assert preserved == original and new_ids == []
    duplicate = original.replace(assigned[1], assigned[0])
    with pytest.raises(OfficeError):
        sanitize_fragment(duplicate, _preserve_office_ids=True)


def test_slide_html_byte_limit_is_enforced() -> None:
    with pytest.raises(OfficeError) as error:
        sanitize_fragment("<p>too large</p>", max_bytes=4)
    assert error.value.code is ErrorCode.RESOURCE_TOO_LARGE
