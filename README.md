# SwiftDeploy — Manifest-Driven Deployment & Policy Enforcement Platform

SwiftDeploy is a declarative DevOps platform that builds, configures, deploys, monitors, and governs application infrastructure from a single source of truth: `manifest.yml`.

Instead of manually maintaining infrastructure configuration files, SwiftDeploy dynamically generates infrastructure artifacts, deploys services, exposes observability metrics, enforces operational policies through Open Policy Agent (OPA), and provides deployment safety automation.

---

# Overview

SwiftDeploy transforms a manifest file into a fully operational deployment stack.

The platform:

- Generates `docker-compose.yml`
- Generates `nginx.conf`
- Deploys application infrastructure
- Exposes Prometheus metrics
- Enforces policy-gated deployments
- Enforces policy-gated promotions
- Supports canary/stable deployments
- Provides operational audit reporting
- Tracks runtime telemetry in real-time

All deployment artifacts are dynamically derived from the manifest.

No infrastructure file is manually maintained.

---

# Extended Architecture (Stage 4B)

Stage 4B extends SwiftDeploy from deployment automation into an observability-aware deployment platform.

The system introduces:

- Prometheus metrics instrumentation
- Open Policy Agent (OPA)
- Canary deployment safety checks
- Infrastructure policy enforcement
- Operational audit logging
- Real-time status monitoring

---

# System Architecture

```text
                ┌────────────────────┐
                │    manifest.yml    │
                └─────────┬──────────┘
                          │
                          ▼
                 ┌────────────────┐
                 │ swiftdeploy CLI │
                 └───────┬────────┘
                         │
         ┌───────────────┴────────────────┐
         │                                │
         ▼                                ▼
 ┌──────────────┐                ┌────────────────┐
 │ Generated    │                │ Policy Engine  │
 │ Config Files │                │      OPA       │
 └──────┬───────┘                └────────┬───────┘
        │                                 │
        ▼                                 │
 ┌──────────────┐                         │
 │ Docker Stack │                         │
 └──────┬───────┘                         │
        │                                 │
        ▼                                 │
 ┌──────────────┐─────────────────────────┘
 │ Nginx Ingress│
 └──────┬───────┘
        │
        ▼
 ┌──────────────┐
 │ FastAPI App  │
 └──────┬───────┘
        │
        ▼
 ┌──────────────┐
 │ /metrics     │
 │ Prometheus   │
 └──────────────┘
```

---

# Architecture Principles

SwiftDeploy follows strict separation of concerns:

- CLI handles orchestration and telemetry collection
- OPA handles policy decisions
- Nginx handles ingress traffic
- FastAPI handles application runtime logic

The CLI never directly decides:

- whether deployment is allowed
- whether promotion is safe

All operational decisions are delegated to OPA policies.

---

# Project Structure

```text
.
├── manifest.yml
├── swiftdeploy
├── Dockerfile
├── requirements.txt
├── README.md
├── history.jsonl
├── audit_report.md
├── nginx.conf                # generated
├── docker-compose.yml        # generated
├── policies/
│   ├── infra.rego
│   └── canary.rego
├── templates/
│   ├── docker-compose.tpl
│   └── nginx.conf.tpl
└── app/
    ├── main.py
    └── requirements.txt
```

> All generated files are created in the root directory as required.

---

# Setup & Installation

## 1. Clone Repository

```bash
git clone <your-repository-url>
cd <project-folder>
```

---

## 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

Install CLI dependencies:

```bash
pip install -r requirements.txt
```

Install application dependencies:

```bash
pip install -r app/requirements.txt
```

---

## 4. Verify Docker Installation

```bash
docker --version
docker compose version
```

---

## 5. Build Docker Image

```bash
docker build -t swift-deploy-1-node:latest .
```

---

# Manifest (Single Source of Truth)

Example:

```yaml
services:
  image: swift-deploy-1-node:latest
  port: 3000
  mode: canary
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
  strategy: canary
  restart_policy: unless-stopped
  health_check_timeout: 60
  health_check_path: /healthz
```

---

# Required Manifest Base Structure

The following structure must remain present:

```yaml
services:
  image: swift-deploy-1-node:latest
  port: 3000

nginx:
  image: nginx:latest
  port: 8080

network:
  name: swiftdeploy-net
  driver_type: bridge
```

---

# Important Configuration Rule

```text
services.mode MUST equal deployment.strategy
```

This is enforced during validation.

---

# CLI Commands

---

## Initialize Configuration

```bash
./swiftdeploy init
```

Generates:

- `docker-compose.yml`
- `nginx.conf`

---

## Validate Configuration

```bash
./swiftdeploy validate
```

Checks:

- manifest existence
- YAML validity
- required fields
- Docker image existence
- port availability
- generated configuration validity

---

## Deploy Stack

```bash
./swiftdeploy deploy
```

Deployment workflow:

1. Runs infrastructure policy checks
2. Evaluates OPA policies
3. Generates configuration files
4. Starts containers
5. Waits for `/healthz`
6. Confirms deployment readiness

Deployment automatically fails if infrastructure policies are violated.

---

## Promote Deployment

```bash
./swiftdeploy promote stable
./swiftdeploy promote canary
```

Promotion workflow:

1. Scrapes `/metrics`
2. Calculates:
   - error rate
   - P99 latency

3. Sends telemetry to OPA
4. Evaluates canary safety policies
5. Blocks unsafe promotions
6. Updates deployment mode

---

## Live Status Dashboard

```bash
./swiftdeploy status
```

Displays:

- requests/sec
- error rate
- P99 latency
- infrastructure policy status
- canary policy status

The dashboard refreshes continuously and appends telemetry to:

```text
history.jsonl
```

---

## Generate Audit Report

```bash
./swiftdeploy audit
```

Parses:

- `history.jsonl`

Generates:

- `audit_report.md`

The report includes:

- deployment timeline
- operational telemetry
- policy evaluation results
- policy violations

---

## Teardown Stack

```bash
./swiftdeploy teardown
```

Removes:

- containers
- networks
- volumes

---

# API Service

The application is built with FastAPI.

---

# API Endpoints

## GET /

Returns application metadata.

Example:

```json
{
  "message": "Welcome to SwiftDeploy API",
  "mode": "stable",
  "version": "1.0.0",
  "timestamp": "2026-05-05T11:18:52.229329"
}
```

---

## GET /healthz

Health check endpoint.

Example:

```json
{
  "status": "ok",
  "uptime": 123
}
```

---

## GET /metrics

Prometheus-compatible metrics endpoint.

Example metrics:

```text
http_requests_total
http_request_duration_seconds
app_uptime_seconds
app_mode
chaos_active
```

---

## POST /chaos

Chaos injection endpoint.

Examples:

```json
{ "mode": "slow", "duration": 3 }
```

```json
{ "mode": "error", "rate": 0.5 }
```

```json
{ "mode": "recover" }
```

---

# Metrics & Observability

SwiftDeploy exposes Prometheus telemetry for operational monitoring.

---

# Metrics Tracked

## Throughput & Errors

```text
http_requests_total
```

Tracks:

- request count
- request method
- request path
- status code

---

## Latency

```text
http_request_duration_seconds
```

Histogram-based latency metric used for:

- percentile analysis
- P99 calculation
- deployment safety evaluation

---

## Runtime State

```text
app_uptime_seconds
app_mode
chaos_active
```

Tracks:

- uptime
- deployment mode
- active chaos state

---

# Why Histograms Were Used

Histograms expose percentile-based latency metrics such as P99.

Average latency alone can hide tail latency spikes and unstable runtime behavior.

P99 latency provides significantly stronger deployment safety visibility.

---

# Policy Engine (OPA)

SwiftDeploy integrates Open Policy Agent (OPA) for policy enforcement.

OPA evaluates:

- infrastructure readiness
- deployment safety
- canary health

The CLI gathers telemetry and operational context, but OPA exclusively owns policy decisions.

---

# Infrastructure Policies

Infrastructure policies evaluate:

- disk availability
- CPU load

Deployment is denied if:

- Disk Free < 10GB
- CPU Load > 2.0

---

# Canary Safety Policies

Canary policies evaluate:

- error rate
- P99 latency

Promotion is denied if:

- Error Rate > 1%
- P99 Latency > 500ms

---

# Policy Isolation

OPA is intentionally isolated from public ingress.

- OPA is not exposed through Nginx
- OPA communicates internally only
- Policies remain inaccessible externally

This reduces attack surface exposure and improves operational safety.

---

# Deployment Safety Workflow

## Pre-Deploy

Before deployment:

1. CLI gathers host metrics
2. Metrics are sent to OPA
3. OPA evaluates infrastructure policies
4. Deployment proceeds only if policies pass

---

## Pre-Promote

Before promotion:

1. CLI scrapes live metrics
2. Error rate is calculated
3. P99 latency is calculated
4. Metrics are sent to OPA
5. OPA evaluates canary safety
6. Promotion proceeds only if policies pass

---

# Nginx Features

- Reverse proxy to FastAPI app
- Custom deployment headers
- Health check routing
- JSON error responses
- Access log formatting

---

# Nginx Access Log Format

```text
$time_iso8601 | $status | ${request_time}s | $upstream_addr | $request
```

---

# Security Features

- Non-root app container
- Dropped Linux capabilities
- Restart policies
- Internal Docker networking
- OPA isolation
- Health checks
- Volume-based logging

---

# Example Usage

## Validate

```bash
./swiftdeploy validate
```

---

## Deploy

```bash
./swiftdeploy deploy
```

---

## Promote

```bash
./swiftdeploy promote stable
```

---

## Monitor

```bash
./swiftdeploy status
```

---

## Audit

```bash
./swiftdeploy audit
```

---

# Logs

Generate traffic:

```bash
for i in {1..10}; do curl http://localhost:8080/; done
```

View logs:

```bash
docker logs swiftdeploy-nginx
```

---

# Design Decisions

Key architectural decisions made during implementation:

- Manifest-driven infrastructure
- Policy isolation through OPA
- Ingress-based telemetry scraping
- Ephemeral policy evaluations
- Histogram-based latency tracking
- Canary safety enforcement
- Audit-first operational visibility

---

# Key Features

- Declarative infrastructure
- Dynamic configuration generation
- Automated deployments
- Canary deployments
- Policy-gated promotions
- Observability-driven safety checks
- Prometheus instrumentation
- OPA policy enforcement
- Live operational dashboard
- Audit reporting

---

# Conclusion

SwiftDeploy evolved from a deployment automation utility into an observability-aware deployment platform.

The platform now combines:

- deployment orchestration
- runtime telemetry
- policy enforcement
- canary safety
- operational auditing

All infrastructure, deployment behavior, and operational decisions are derived from a single declarative manifest.

---

# Author

Nsikak Sunday
