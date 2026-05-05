def validate_config(config):
    app = config["app"]
    nginx = config["nginx"]
    network = config["network"]
    deployment = config["deployment"]

    if not app.get("image") or not app.get("port") or not app.get("mode"):
        raise ValueError("App section missing required fields")
    if app["mode"] not in {"stable", "canary"}:
        raise ValueError("App mode must be stable or canary")

    if not nginx.get("image") or not nginx.get("port"):
        raise ValueError("Nginx section missing required fields")

    if not network.get("name"):
        raise ValueError("Network section missing name")

    if app["mode"] != deployment.get("strategy"):
        raise ValueError("App mode and deployment strategy must match")

    return True
