{
  description = "Nano-like LLM Editor Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python313
            uv
            # Add rust here if we decide to use it later
            # rustc
            # cargo
          ];

          shellHook = ''
            echo "Welcome to the Nano-like LLM Editor dev environment!"
            echo "Python version: $(python3 --version)"
            echo "uv version: $(uv --version)"
          '';
        };
      }
    );
}
