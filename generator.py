from config_loader import load_manifest, normalize_manifest
from derived import derive_values
from validation import validate_config
from renderer import render_template

def main():
    manifest = load_manifest()
    config = normalize_manifest(manifest)
    derived = derive_values(config)
    config["derived"] = derived
    validate_config(config)

    docker_compose = render_template("templates/docker-compose.tpl", {
        "app_image": config["app"]["image"],
        "app_container": derived["app_container"],
        "mode": config["app"]["mode"],
        "app_port": config["app"]["port"],
        "app_version": config["app"]["version"],
        "log_volume": derived["log_volume"],
        "nginx_image": config["nginx"]["image"],
        "nginx_container": derived["nginx_container"],
        "nginx_port": config["nginx"]["port"],
        "network_name": config["network"]["name"],
        "network_driver": config["network"]["driver_type"],
        "restart_policy": config["deployment"]["restart_policy"],
    })
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose)

    nginx_conf = render_template("templates/nginx.conf.tpl", {
        "app_port": config["app"]["port"],
        "proxy_timeout": config["nginx"]["proxy_timeout"],
        "log_format": "combined",
        "x_deployed_by": config["nginx"]["headers"].get("X-Deployed-By"),
        "mode": config["app"]["mode"],
        "error": derived["error_json"]["error"],
        "code": derived["error_json"]["code"],
        "service": derived["error_json"]["service"],
        "contact": derived["error_json"]["contact"],
    })
    with open("nginx.conf", "w") as f:
        f.write(nginx_conf)

if __name__ == "__main__":
    main()
