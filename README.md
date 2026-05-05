# SwiftDeploy — Manifest-Driven Deployment Tool

SwiftDeploy is a declarative DevOps tool that builds, configures, and deploys an application stack from a single source of truth: `manifest.yml`.

Instead of manually writing infrastructure configuration files, SwiftDeploy generates everything automatically and manages the full lifecycle of the deployment.

---

## Overview

SwiftDeploy takes a manifest file and:

- Generates `docker-compose.yml` and `nginx.conf`
- Deploys containers using Docker Compose
- Manages application lifecycle (deploy, promote, teardown)
- Enforces configuration validation before deployment
- Supports canary and stable deployment modes

The system ensures that nothing is manually configured — all outputs are derived from the manifest.

---

## Architecture

```
Client Request
      ↓
   Nginx (Reverse Proxy)
      ↓
   App Container (FastAPI)
```

```
manifest.yml
      ↓
swiftdeploy CLI
      ↓
Generated Configs (root folder)
      ↓
Docker Compose
      ↓
Running Containers
```

---

## Project Structure

```
.
├── manifest.yml
├── swiftdeploy
├── Dockerfile
├── app/
│   ├── main.py
│   └── requirements.txt
├── templates/
│   ├── docker-compose.tpl
│   └── nginx.conf.tpl
├── docker-compose.yml        # generated
├── nginx.conf                # generated
└── README.md
```

> All generated files are placed in the **root directory** as required.

---

## Setup & Installation

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd <project-folder>
```

---

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

Install **CLI dependencies**:

```bash
pip install requests pyyaml
```

Install **application dependencies**:

```bash
pip install -r app/requirements.txt
```

---

### 4. Ensure Docker is Installed

```bash
docker --version
docker compose version
```

---

### 5. Build Docker Image

```bash
docker build -t swift-deploy-node-unique:latest .
```

---

## Manifest (Single Source of Truth)

Example:

```yaml
services:
  image: swift-deploy-node-unique:latest
  port: 3000
  mode: stable
  version: 1.0.0

nginx:
  image: nginx:latest
  port: 8080
  proxy_timeout: 5
  headers:
    X-Deployed-By: swiftdeploy

network:
  name: swiftdeploy-net
  driver_type: bridge

deployment:
  strategy: stable
  restart_policy: unless-stopped
  health_check_timeout: 60
  health_check_path: /healthz
```

### Important Rule

```
services.mode MUST equal deployment.strategy
```

This is enforced during validation.

---

## CLI Commands

### Initialize (Generate Configs)

```bash
./swiftdeploy init
```

Generates:

- `docker-compose.yml`
- `nginx.conf`

---

### Validate Configuration

```bash
./swiftdeploy validate
```

Checks:

- manifest exists and is valid YAML
- required fields are present
- Docker image exists locally
- Nginx port availability
- nginx.conf syntax

---

### Deploy Stack

```bash
./swiftdeploy deploy
```

- Runs `init`
- Starts containers
- Waits for `/healthz`
- Fails if service is not ready within timeout

---

### Promote Deployment Mode

```bash
./swiftdeploy promote canary
./swiftdeploy promote stable
```

- Updates manifest
- Regenerates configs
- Restarts only the app container
- Verifies health after switch

---

### Teardown

```bash
./swiftdeploy teardown
```

Removes:

- containers
- networks
- volumes

---

## API Service

Built with FastAPI.

### Endpoints

#### GET /

```json
{
  "message": "Welcome to SwiftDeploy API",
  "mode": "stable | canary",
  "version": "1.0.0",
  "timestamp": "..."
}
```

---

#### GET /healthz

```json
{
  "status": "ok",
  "uptime": 123
}
```

---

#### POST /chaos (canary only)

```json
{ "mode": "slow", "duration": 3 }
{ "mode": "error", "rate": 0.5 }
{ "mode": "recover" }
```

---

## Nginx Features

- Reverse proxy to app container

- Adds header:

  ```
  X-Deployed-By: swiftdeploy
  ```

- Forwards `X-Mode` from upstream

- Custom access log format:

```
$time_iso8601 | $status | ${request_time}s | $upstream_addr | $request
```

- JSON error responses for 502/503/504

---

## Docker & Security

- App container runs as non-root user
- Linux capabilities dropped
- Restart policy enforced
- Named volumes used for logs
- Health check configured via `/healthz`

### Note on Nginx

Nginx runs as root to bind to port 80 internally.
The application container enforces non-root execution for security.

---

## Build & Run

```bash
./swiftdeploy validate
./swiftdeploy deploy
```

Test:

```bash
curl http://localhost:8080/
curl http://localhost:8080/healthz
```

---

## Logs

Generate traffic:

```bash
for i in {1..10}; do curl http://localhost:8080/; done
```

View logs:

```bash
docker exec -it swiftdeploy-nginx cat /var/log/nginx/access.log
```

---

## Screenshots (Submission Requirement)

Include:

- validate output
- deploy success output
- promote + health check
- generated `docker-compose.yml`
- generated `nginx.conf`
- nginx access logs

---

## Design Decisions

- Manifest is the single source of truth
- No manual configuration files are written
- CLI enforces system consistency before deployment
- Canary mode enables runtime behavior testing
- Deployment lifecycle is fully automated

---

## Key Features

- Declarative infrastructure
- Automated config generation
- Zero manual setup after manifest definition
- Canary deployment support
- Health-based deployment validation

---

## Conclusion

SwiftDeploy demonstrates how a single declarative manifest can control:

- infrastructure
- deployment
- runtime behavior

All system components are derived, validated, and orchestrated automatically.

---

## Author

Nsikak Sunday
