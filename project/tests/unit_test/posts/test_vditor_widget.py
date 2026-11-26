from pathlib import Path

from posts.widgets import VditorWidget


def test_vditor_widget_loads_the_editor_assets() -> None:
    assert VditorWidget.Media.css["all"] == (
        "https://cdn.jsdelivr.net/npm/vditor@3.11.1/dist/index.css",
    )
    assert VditorWidget.Media.js == (
        "https://cdn.jsdelivr.net/npm/vditor@3.11.1/dist/index.min.js",
        "posts/vditor.js",
    )


def test_vditor_widget_marks_its_textarea_for_initialization() -> None:
    rendered = VditorWidget().render("content", "# Heading", {"id": "id_content"})

    assert 'data-vditor="true"' in rendered
    assert 'data-vditor-upload-url="/api/attachments/upload/"' in rendered
    assert "# Heading" in rendered


def test_vditor_is_configured_in_english() -> None:
    script = (Path(__file__).parents[3] / "posts/static/posts/vditor.js").read_text()

    assert 'lang: "en_US"' in script


def test_vditor_uses_a_simple_resizable_editor_without_preview() -> None:
    script = (Path(__file__).parents[3] / "posts/static/posts/vditor.js").read_text()

    assert "height: 500" in script
    assert 'mode: "ir"' in script
    assert 'resize: { enable: true, position: "bottom" }' in script
    assert '"headings"' in script
    assert '"bold"' in script
    assert '"italic"' in script
    assert '"list"' in script
    assert '"ordered-list"' in script
    assert '"upload"' in script
    assert '"preview"' not in script


def test_vditor_uploads_include_the_django_csrf_token() -> None:
    script = (Path(__file__).parents[3] / "posts/static/posts/vditor.js").read_text()

    assert 'input[name="csrfmiddlewaretoken"]' in script
    assert 'getCookie("csrftoken")' in script
    assert '"X-CSRFToken": csrfToken' in script
