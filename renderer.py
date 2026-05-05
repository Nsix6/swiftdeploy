def render_template(template_path, values):
    with open(template_path, "r") as f:
        content = f.read()
    for key, val in values.items():
        placeholder = "{{" + key + "}}"
        content = content.replace(placeholder, str(val))
    return content
