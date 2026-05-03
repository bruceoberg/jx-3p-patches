#!/usr/bin/env zsh
#
# shell.zsh — one-shot dev environment installer for non-Nix macOS users.
#
# Installs everything declared in shell.nix (clang, gnumake, libsndfile, uv)
# via Xcode Command Line Tools and Homebrew. Idempotent — safe to re-run.
#
# Usage:
#     ./shell.zsh
#
# After this finishes successfully, run `make` to build the C tools and run
# the Python tests.

set -e
set -u

print_step() {
    print -P "%F{cyan}==>%f $1"
}

print_done() {
    print -P "%F{green}✓%f $1"
}

print_warn() {
    print -P "%F{yellow}!%f $1"
}

print_err() {
    print -P "%F{red}✗%f $1" >&2
}

# 1. macOS only -------------------------------------------------------------
if [[ "$(uname)" != "Darwin" ]]; then
    print_err "This script targets macOS. On Linux, see the README for apt/dnf instructions."
    exit 1
fi

# 2. Xcode Command Line Tools (clang + make) --------------------------------
print_step "Checking for Xcode Command Line Tools..."
if xcode-select -p &>/dev/null; then
    print_done "Xcode Command Line Tools already installed at $(xcode-select -p)"
else
    print_warn "Xcode Command Line Tools not found. Triggering installer..."
    xcode-select --install || true
    print_warn "A GUI dialog should have appeared. Finish the install, then re-run this script."
    exit 1
fi

# 3. Homebrew ---------------------------------------------------------------
print_step "Checking for Homebrew..."
if ! command -v brew &>/dev/null; then
    # Try the standard install paths in case brew is installed but not on PATH
    if [[ -x /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -x /usr/local/bin/brew ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
fi

if ! command -v brew &>/dev/null; then
    print_warn "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    if [[ -x /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -x /usr/local/bin/brew ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    else
        print_err "Homebrew installed but the brew binary wasn't found. Open a new terminal and re-run."
        exit 1
    fi
fi
print_done "Homebrew available at $(command -v brew)"

# 4. Brew packages (mirrors shell.nix) --------------------------------------
# Note: clang and make come from Xcode CLT above; brew packages are libsndfile
# and uv. If you'd prefer GNU make over Apple's BSD-flavored bsdmake, also
# `brew install make` and use `gmake`.
brew_packages=(libsndfile uv)

print_step "Installing/updating brew packages: ${brew_packages[*]}"
for pkg in "${brew_packages[@]}"; do
    if brew list --formula "$pkg" &>/dev/null; then
        print_done "$pkg already installed"
    else
        brew install "$pkg"
        print_done "$pkg installed"
    fi
done

# 5. Summary ----------------------------------------------------------------
print_step "Summary"
print "  clang:      $(clang --version | head -1)"
print "  make:       $(make --version | head -1)"
print "  libsndfile: $(brew --prefix libsndfile)"
print "  uv:         $(uv --version)"

cat <<'EOF'

All set. Next steps:

    make            # build the C tools and run Python tests
    make install    # install the `jx3p` CLI on your PATH

EOF
