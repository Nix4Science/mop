{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/23.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs }:
    (flake-utils.lib.eachDefaultSystem (system:
      let pkgs = import nixpkgs { inherit system; };
      in {
        packages = rec {
          default = mop;
          mop = pkgs.python3Packages.buildPythonApplication {
            pname = "mop";
            version = "0.0.0";
            src = ./.;
            propagatedBuildInputs = with python3Packages; [ pyyaml requests ];
          };
        };
      }));
}
