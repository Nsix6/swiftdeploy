import yaml

def load_manifest(path="manifest.yml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def normalize_manifest(manifest):
    services = manifest.get("services", {})
    nginx = manifest.get("nginx", {})
    network = manifest.get("network", {})
    deployment = manifest.get("deployment", {})

    return {
        "app": {
            "image": services.get("image"),
            "port": services.get("port"),
            "mode": services.get("mode"),
            "version": services.get("version"),
        },
        "nginx": {
            "image": nginx.get("image"),
            "port": nginx.get("port"),
            "proxy_timeout": nginx.get("proxy_timeout"),
            "headers": nginx.get("headers", {}),
            "error_handling": nginx.get("error_handling", {}),
        },
        "network": {
            "name": network.get("name"),
            "driver_type": network.get("driver_type"),
        },
        "deployment": {
            "strategy": deployment.get("strategy"),
            "health_check_path": deployment.get("health_check_path"),
            "health_check_timeout": deployment.get("health_check_timeout"),
            "restart_policy": deployment.get("restart_policy"),
        }
    }
