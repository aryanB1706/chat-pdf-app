#!/usr/bin/env bash
# EC2 deploy for the agentic Chat-PDF backend (FastAPI + pgvector + Redis + Celery).
# Run on a fresh Ubuntu 22.04/24.04 instance (t3.medium+ recommended for 500-page PDFs).
#
#   1. Point your repo URL below, copy this host change if needed, then run:
#        chmod +x deploy/ec2-setup.sh && sudo ./deploy/ec2-setup.sh
#   2. The API lands on http://<EC2_PUBLIC_IP>:8000  (docs at /docs)
#   3. Re-deploy later with:  git pull && docker-compose up --build -d
set -euo pipefail

REPO_URL="${REPO_URL:-YOUR_REPO_URL_HERE}"   # e.g. https://github.com/<you>/chat-pdf-app.git
APP_DIR="/opt/chat-pdf-app"

if [ "$EUID" -ne 0 ]; then echo "Run as root: sudo ./deploy/ec2-setup.sh"; exit 1; fi

# --- Docker ---
if ! command -v docker >/dev/null; then
  apt-get update -y
  apt-get install -y docker.io docker-compose-plugin
  systemctl enable --now docker
fi
COMPOSE="docker compose"
if ! docker compose version >/dev/null 2>&1; then COMPOSE="docker-compose"; fi

# --- App ---
if [ ! -d "$APP_DIR/.git" ]; then git clone "$REPO_URL" "$APP_DIR"; fi
cd "$APP_DIR"

# --- Env (GEMINI_API_KEY optional but recommended) ---
if [ ! -f .env ]; then
  echo "GEMINI_API_KEY=${GEMINI_API_KEY:-}" > .env
  echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)" >> .env
fi

# --- Firewall hint (Security Group must allow 8000 + 22) ---
ufw allow 8000/tcp >/dev/null 2>&1 || true

$COMPOSE up --build -d
sleep 5
$COMPOSE ps
curl -sf http://localhost:8000/health && echo "DEPLOY_OK: API healthy"
