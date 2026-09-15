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
    assert "# Heading" in rendered
