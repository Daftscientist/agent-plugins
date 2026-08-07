import pytest
from bs4 import BeautifulSoup

from office_mcp.domain.html import parse_styles, sanitize_fragment, select_element, visible_text
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
        "<img src='data:image/svg+xml;base64,PHN2Zz48L3N2Zz4='>",
        '<div style="background-image:u\\72l(https://example.com/x.png)">x</div>',
    ],
)
def test_active_html_is_rejected(html: str) -> None:
    with pytest.raises(OfficeError) as error:
        sanitize_fragment(html)
    assert error.value.code is ErrorCode.UNSAFE_HTML


def test_server_replaces_spoofed_ids_and_strips_classes() -> None:
    result, assigned = sanitize_fragment(
        '<section data-office-id="el_attacker" data-domoxml-preserved-payload="attacker" '
        'data-transition="morph" '
        'class="styled"><h1>x</h1></section>'
    )
    assert "el_attacker" not in result
    assert "data-domoxml" not in result
    assert "data-transition" not in result
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


@pytest.mark.parametrize(
    "html",
    [
        "<p>kept</p>TRAILING-VISIBLE-TEXT",
        "LEADING-VISIBLE-TEXT<p>kept</p>",
        "<p>a</p>BETWEEN<p>b</p>",
        "<!-- a stray comment --><p>kept</p>",
    ],
)
def test_stray_sibling_text_is_rejected_not_silently_dropped(html: str) -> None:
    with pytest.raises(OfficeError) as error:
        sanitize_fragment(html)
    assert error.value.code is ErrorCode.INVALID_HTML


@pytest.mark.parametrize(
    "html",
    [
        "  <p>kept</p>  ",
        "\n<p>kept</p>\n",
        "<p>a</p> <p>b</p>",
    ],
)
def test_insignificant_whitespace_around_roots_is_still_accepted(html: str) -> None:
    result, _ = sanitize_fragment(html)
    assert "kept" in result or ("a</p>" in result and "b</p>" in result)


def test_only_closed_document_assets_and_safe_links_are_allowed() -> None:
    result, _ = sanitize_fragment(
        '<section><img src="data:image/png;base64,'
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/"
        'pLvAAAAAElFTkSuQmCC">'
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


def test_model_facing_html_hides_domoxml_preservation_payloads() -> None:
    from office_mcp.domain.html import model_facing_html

    source = '<div data-office-id="el_12345678" data-domoxml-text-payload="secret">x</div>'
    assert "data-domoxml" not in model_facing_html(source)
    assert "el_12345678" in model_facing_html(source)


def test_slide_html_byte_limit_is_enforced() -> None:
    with pytest.raises(OfficeError) as error:
        sanitize_fragment("<p>too large</p>", max_bytes=4)
    assert error.value.code is ErrorCode.RESOURCE_TOO_LARGE


def test_visible_text_excludes_display_none() -> None:
    text = visible_text('<div>Visible</div><div style="display:none">Hidden</div>')
    assert "Visible" in text
    assert "Hidden" not in text


def test_visible_text_excludes_visibility_hidden() -> None:
    text = visible_text('<div>Visible</div><div style="visibility:hidden">Hidden</div>')
    assert "Visible" in text
    assert "Hidden" not in text


def test_visible_text_excludes_hidden_attribute() -> None:
    text = visible_text("<div>Visible</div><div hidden>Hidden</div>")
    assert "Visible" in text
    assert "Hidden" not in text


def test_visible_text_excludes_descendants_of_hidden_ancestor() -> None:
    text = visible_text('<div style="display:none"><p>Outer</p><span>Inner</span></div>')
    assert "Outer" not in text
    assert "Inner" not in text


def test_visible_text_still_returns_ordinary_visible_descendants() -> None:
    text = visible_text(
        '<section><h1>Title</h1><div style="display:none">Gone</div>'
        "<p>Kept <b>nested</b> text</p></section>"
    )
    assert "Title" in text
    assert "Kept" in text
    assert "nested" in text
    assert "Gone" not in text
