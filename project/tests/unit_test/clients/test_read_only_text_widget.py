from clients.widgets.read_only_text.widget import ReadOnlyTextWidget


def test_widget_renders_value_and_hidden_input() -> None:
    widget = ReadOnlyTextWidget()

    html = widget.render("secret", "my-secret-value")

    assert "my-secret-value" in html
    assert '<input type="hidden" name="secret" value="my-secret-value">' in html
    assert '<div class="form-control-static">' in html


def test_widget_renders_copy_button_when_enabled() -> None:
    widget = ReadOnlyTextWidget(copy_button=True)

    html = widget.render("secret", "my-secret-value")

    assert "Copy" in html
    assert "copy-text" in html


def test_widget_does_not_render_copy_button_by_default() -> None:
    widget = ReadOnlyTextWidget()

    html = widget.render("secret", "my-secret-value")

    assert "Copy" not in html


def test_widget_renders_custom_display_tag() -> None:
    widget = ReadOnlyTextWidget(tag="span")

    html = widget.render("secret", "my-secret-value")

    assert "<span" in html
