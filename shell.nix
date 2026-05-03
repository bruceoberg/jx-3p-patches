with (import <nixpkgs> {});
mkShell {
  packages = [
    clang
    gnumake
    libsndfile
    uv
  ];
}
