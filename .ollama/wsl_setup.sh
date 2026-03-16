#!/usr/bin/env bash
set -euo pipefail

# ClaudeClockwork WSL + Ollama workstation setup.
# Safe to re-run. Writes WSL, environment and systemd configuration in a predictable way.
# Project-facing comments are in English on purpose.

WIN_USER="${WIN_USER:-YvesT}"
WSL_RAM="${WSL_RAM:-56GB}"
WSL_PROCESSORS="${WSL_PROCESSORS:-16}"
WSL_SWAP="${WSL_SWAP:-8GB}"
OLLAMA_MODELS_PATH="${OLLAMA_MODELS_PATH:-/mnt/e/OllamaModels/.ollama}"
OLLAMA_LOAD_TIMEOUT="${OLLAMA_LOAD_TIMEOUT:-20m}"
OLLAMA_BIND_HOST="${OLLAMA_BIND_HOST:-0.0.0.0:11434}"
OLLAMA_NUM_THREADS="${OLLAMA_NUM_THREADS:-16}"
OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:-30m}"
OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-1}"
PYTHON_ALIAS="${PYTHON_ALIAS:-python-is-python3}"

CHECK_ONLY=false
SKIP_OLLAMA=false
SKIP_SYSTEMD=false
LOCAL_ONLY=false

for arg in "$@"; do
  case "$arg" in
    --check) CHECK_ONLY=true ;;
    --skip-ollama) SKIP_OLLAMA=true ;;
    --skip-systemd) SKIP_SYSTEMD=true ;;
    --local-only) LOCAL_ONLY=true ;;
    *) ;;
  esac
done

if $LOCAL_ONLY; then
  OLLAMA_BIND_HOST="127.0.0.1:11434"
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ok()  { echo -e "     ${GREEN}✓${NC}  $1"; }
err() { echo -e "     ${RED}✗${NC}  $1"; }
inf() { echo -e "     ${BLUE}ℹ${NC}  $1"; }
wn()  { echo -e "     ${YELLOW}⚠${NC}  $1"; }
ph()  {
  echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
  echo -e "  $1"
  echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
}

set_env() {
  local key="$1"
  local value="$2"
  local file="/etc/environment"

  if [ ! -f "$file" ]; then
    sudo touch "$file"
  fi

  if grep -q "^${key}=" "$file" 2>/dev/null; then
    local current
    current=$(grep "^${key}=" "$file" | cut -d= -f2-)
    if [ "$current" = "$value" ]; then
      ok "${key}=${value} (already set)"
    else
      sudo sed -i "s|^${key}=.*|${key}=${value}|" "$file"
      ok "${key}=${value} (updated from ${current})"
    fi
  else
    echo "${key}=${value}" | sudo tee -a "$file" > /dev/null
    ok "${key}=${value} (new)"
  fi
}

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║           ClaudeClockwork — WSL + Ollama Workstation Setup           ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"

if $CHECK_ONLY; then
  wn "CHECK MODE — no changes will be written"
fi

ph "0 / 6  —  Host overview"
inf "Kernel:   $(uname -r)"
inf "User:     $(whoami)"
inf "WSL RAM:  ${WSL_RAM}"
inf "CPU:      ${WSL_PROCESSORS}"
inf "Swap:     ${WSL_SWAP}"
inf "Models:   ${OLLAMA_MODELS_PATH}"
inf "Bind:     ${OLLAMA_BIND_HOST}"

ph "1 / 6  —  /etc/environment"
if $CHECK_ONLY; then
  inf "Current /etc/environment:"
  cat /etc/environment || true
else
  set_env "GGML_CUDA_NO_PINNED" "1"
  set_env "OLLAMA_MODELS" "$OLLAMA_MODELS_PATH"
  set_env "OLLAMA_LOAD_TIMEOUT" "$OLLAMA_LOAD_TIMEOUT"
  set_env "OLLAMA_FLASH_ATTENTION" "1"
  set_env "OLLAMA_NUM_THREADS" "$OLLAMA_NUM_THREADS"
  set_env "OLLAMA_NUM_PARALLEL" "$OLLAMA_NUM_PARALLEL"
  set_env "OLLAMA_KEEP_ALIVE" "$OLLAMA_KEEP_ALIVE"
  set_env "OLLAMA_HOST" "$OLLAMA_BIND_HOST"
  inf "Updated /etc/environment:"
  cat /etc/environment
fi

ph "2 / 6  —  Windows-side .wslconfig"
WSLCONFIG_PATH="/mnt/c/Users/${WIN_USER}/.wslconfig"
WSLCONFIG_CONTENT="[wsl2]
memory=${WSL_RAM}
processors=${WSL_PROCESSORS}
swap=${WSL_SWAP}
gpuSupport=true
localhostForwarding=true"

if $CHECK_ONLY; then
  inf "Expected path: ${WSLCONFIG_PATH}"
  if [ -f "$WSLCONFIG_PATH" ]; then
    cat "$WSLCONFIG_PATH"
  else
    wn "Missing: ${WSLCONFIG_PATH}"
  fi
else
  if [ -f "$WSLCONFIG_PATH" ]; then
    cp "$WSLCONFIG_PATH" "${WSLCONFIG_PATH}.bak"
    ok "Backup created: ${WSLCONFIG_PATH}.bak"
  fi
  echo "$WSLCONFIG_CONTENT" > "$WSLCONFIG_PATH"
  ok "Written: ${WSLCONFIG_PATH}"
fi

ph "3 / 6  —  /etc/wsl.conf"
WSL_CONF="/etc/wsl.conf"
WSL_CONF_CONTENT="[boot]
systemd=true"
if $CHECK_ONLY; then
  [ -f "$WSL_CONF" ] && cat "$WSL_CONF" || wn "Missing: ${WSL_CONF}"
else
  echo "$WSL_CONF_CONTENT" | sudo tee "$WSL_CONF" > /dev/null
  ok "Written: ${WSL_CONF}"
fi

ph "4 / 6  —  Ollama + python"
if $SKIP_OLLAMA; then
  wn "Ollama install/update skipped"
elif $CHECK_ONLY; then
  command -v ollama >/dev/null 2>&1 && ok "$(ollama --version)" || wn "Ollama not installed"
else
  if command -v ollama >/dev/null 2>&1; then
    ok "Ollama already installed: $(ollama --version)"
  else
    inf "Installing Ollama"
    curl -fsSL https://ollama.ai/install.sh | sh
    ok "Installed: $(ollama --version)"
  fi
fi

if $CHECK_ONLY; then
  command -v python >/dev/null 2>&1 && ok "python -> $(python --version)" || wn "python alias not available"
else
  if dpkg -l "$PYTHON_ALIAS" >/dev/null 2>&1; then
    ok "$PYTHON_ALIAS already installed"
  else
    sudo apt-get update -qq
    sudo apt-get install -y "$PYTHON_ALIAS" >/dev/null
    ok "$PYTHON_ALIAS installed"
  fi
fi

ph "5 / 6  —  systemd service"
SYSTEMD_SERVICE="/etc/systemd/system/ollama.service"
SYSTEMD_CONTENT="[Unit]
Description=Ollama AI Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$(whoami)
Environment=GGML_CUDA_NO_PINNED=1
Environment=OLLAMA_MODELS=${OLLAMA_MODELS_PATH}
Environment=OLLAMA_LOAD_TIMEOUT=${OLLAMA_LOAD_TIMEOUT}
Environment=OLLAMA_FLASH_ATTENTION=1
Environment=OLLAMA_NUM_THREADS=${OLLAMA_NUM_THREADS}
Environment=OLLAMA_NUM_PARALLEL=${OLLAMA_NUM_PARALLEL}
Environment=OLLAMA_KEEP_ALIVE=${OLLAMA_KEEP_ALIVE}
Environment=OLLAMA_HOST=${OLLAMA_BIND_HOST}
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target"

if $SKIP_SYSTEMD; then
  wn "systemd setup skipped"
elif $CHECK_ONLY; then
  [ -f "$SYSTEMD_SERVICE" ] && ok "Service file present" || wn "Missing: ${SYSTEMD_SERVICE}"
  systemctl is-active ollama >/dev/null 2>&1 && ok "ollama.service active" || wn "ollama.service inactive"
else
  echo "$SYSTEMD_CONTENT" | sudo tee "$SYSTEMD_SERVICE" > /dev/null
  sudo systemctl daemon-reload
  sudo systemctl enable ollama >/dev/null 2>&1 && ok "ollama.service enabled" || wn "enable failed"
  sudo systemctl restart ollama >/dev/null 2>&1 && ok "ollama.service restarted" || wn "restart failed"
fi

ph "6 / 6  —  next actions"
cat <<EOF
  1. In PowerShell, run:
     wsl --shutdown

  2. Re-open WSL and verify:
     curl http://127.0.0.1:11434/api/tags

  3. From Windows, verify external bind if you did not use --local-only:
     curl http://<WSL-IP>:11434/api/tags

  4. Run the Clockwork alias builder:
     python ollama_setup.py --summary
     python ollama_setup.py --with-optional

  Notes:
  - OLLAMA_HOST is now explicit (${OLLAMA_BIND_HOST}).
  - Models on /mnt/* are valid but slower for very large loads.
  - For strictly local-only access, rerun this script with --local-only.
EOF
