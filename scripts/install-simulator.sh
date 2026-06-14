#!/usr/bin/env bash
#
# install-simulator.sh — Sintez-2 simulator toolchain installer (Ubuntu 24.04 "noble")
#
# Installs the electronics-simulator side of the project (spec §5.2/§5.3):
#   • ngspice    — SPICE batch engine for the analog corners (PSU, 14 MHz clock, RGB)
#   • SimulIDE   — the visual, real-time TTL simulator (the "movie") + VCD export
#   • AppImage / Qt runtime dependencies needed on noble
#
# KiCad 9 is assumed already installed (it is). Run:
#     bash /home/anatolie/ai3/s4/scripts/install-simulator.sh
#
# Notes
#  - Uses sudo only for the apt step; everything else installs into your $HOME.
#  - SimulIDE 1.x is distributed ONLY via simulide.com (a donation form, amount can
#    be 0) — it is not in apt and not on the old SourceForge mirror. So this script
#    auto-detects a file you downloaded to ~/Downloads. If none is found it prints
#    the exact link and stops at that step (apt + ngspice still get installed).
#
set -euo pipefail

log()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m[ok]\033[0m %s\n' "$*"; }

# ---------------------------------------------------------------------------
# 1. APT packages (analog engine + AppImage/Qt runtime) — needs sudo
# ---------------------------------------------------------------------------
log "Installing apt packages (ngspice + AppImage/Qt runtime deps)…"
sudo apt-get update
sudo apt-get install -y \
    ngspice \
    libfuse2t64 \
    libxcb-cursor0 libxcb-xinerama0 libegl1 libopengl0 \
    wget tar coreutils
#   ngspice         : standalone SPICE (`ngspice -b`) for analog corners (spec §5.3)
#   libfuse2t64     : FUSE2 so .AppImage files run on Ubuntu 24.04
#   libxcb-*/libegl : Qt xcb/opengl runtime SimulIDE needs headlessly/with a GUI
ok "ngspice: $(ngspice --version 2>/dev/null | head -1 || echo 'installed')"

# ---------------------------------------------------------------------------
# 2. SimulIDE (visual simulator)
# ---------------------------------------------------------------------------
INSTALL_DIR="$HOME/.local/opt/simulide"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$DESKTOP_DIR"

log "Looking for a downloaded SimulIDE Linux-64 file in ~/Downloads …"
# Robust: search ONLY ~/Downloads, real files, newest first. (Do not use
# `ls -t <glob>` — with no matches it falls back to listing the cwd.)
mapfile -t FILES < <(find "$HOME/Downloads" -maxdepth 1 -type f \
    \( -iname 'SimulIDE*Lin64*.tar.gz'  -o -iname 'SimulIDE*Lin64*.AppImage' \
       -o -iname 'SimulIDE*linux*.tar.gz' \
       -o -iname 'SimulIDE*.AppImage'   -o -iname 'SimulIDE*.tar.gz' \) \
    -printf '%T@\t%p\n' 2>/dev/null | sort -rn | cut -f2-)

if [ "${#FILES[@]}" -eq 0 ]; then
    warn "No SimulIDE file found in ~/Downloads."
    cat <<'EOF'

    ┌──────────────────────────────────────────────────────────────────────┐
    │  Download SimulIDE 1.1.0-SR2 (Linux 64) once, then re-run this script: │
    │                                                                        │
    │    1. Open:  https://simulide.com/p/downloads/                         │
    │    2. Pick the "Linux 64" build (donation amount can be 0).            │
    │    3. Save the .tar.gz (or .AppImage) into  ~/Downloads/               │
    │    4. Re-run:  bash /home/anatolie/ai3/s4/scripts/install-simulator.sh │
    └──────────────────────────────────────────────────────────────────────┘

EOF
    warn "ngspice is installed; SimulIDE step skipped until the file is present."
    exit 0
fi

SRC="${FILES[0]}"
log "Found: $SRC"

if [[ "$SRC" == *.AppImage ]]; then
    cp -f "$SRC" "$INSTALL_DIR/SimulIDE.AppImage"
    chmod +x "$INSTALL_DIR/SimulIDE.AppImage"
    ln -sf "$INSTALL_DIR/SimulIDE.AppImage" "$BIN_DIR/simulide"
    EXEC="$INSTALL_DIR/SimulIDE.AppImage"
else
    log "Extracting tar.gz into $INSTALL_DIR …"
    rm -rf "$INSTALL_DIR"/SimulIDE_* 2>/dev/null || true
    tar -xzf "$SRC" -C "$INSTALL_DIR"
    # locate the simulide executable inside the extracted tree
    EXEC="$(find "$INSTALL_DIR" -type f -name simulide -perm -u+x 2>/dev/null | head -1)"
    [ -z "$EXEC" ] && EXEC="$(find "$INSTALL_DIR" -type f -name 'simulide*' 2>/dev/null | head -1)"
    if [ -z "$EXEC" ]; then
        warn "Could not find the 'simulide' binary in the extracted folder:"
        find "$INSTALL_DIR" -maxdepth 3 -type f | head -20
        exit 1
    fi
    chmod +x "$EXEC"
    ln -sf "$EXEC" "$BIN_DIR/simulide"
fi
ok "SimulIDE installed → $EXEC"
ok "Launcher → $BIN_DIR/simulide"

# desktop entry (optional convenience)
cat > "$DESKTOP_DIR/simulide.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=SimulIDE
Comment=Real-time electronics simulator (Sintez-2 project)
Exec=$BIN_DIR/simulide %f
Terminal=false
Categories=Development;Electronics;
EOF

# ---------------------------------------------------------------------------
# 3. Verify
# ---------------------------------------------------------------------------
log "Verifying…"
command -v ngspice  >/dev/null && ok "ngspice  → $(command -v ngspice)"
command -v simulide >/dev/null && ok "simulide → $(command -v simulide)  (also: $EXEC)"
echo
ok "Done. Make sure ~/.local/bin is on PATH (echo \$PATH | grep .local/bin)."
echo "    Launch the GUI with:  simulide &"
echo "    Run a SPICE batch with:  ngspice -b your.cir"
