with (import <nixpkgs> {});
mkShell {
  packages = [
    clang
    gnumake
    libsndfile
    uv
  ];

  # Nix's Python wrapper sets VIRTUAL_ENV to the Python install path, which
  # makes `uv run` complain that it doesn't match the project's .venv. Unset
  # it so uv can manage .venv without noise.
  shellHook = ''
    unset VIRTUAL_ENV
  '';
}
