def derive_values(config):
    return {
        "app_container": "swiftdeploy-app",
        "nginx_container": "swiftdeploy-nginx",
        "log_volume": "swiftdeploy-logs",
        "env": {
            "MODE": config["app"]["mode"],
            "APP_PORT": config["app"]["port"],
            "APP_VERSION": config["app"]["version"],
        },
        "error_json": {
            "error": "Service unavailable",
            "code": "502",
            "service": "nginx-proxy",
            "contact": "support@swiftdeploy"
        }
    }
