{ python3Packages }:

python3Packages.buildPythonApplication rec {
    pname = "mop";
    version = "0.0.0";
    src = ./.;
    propagatedBuildInputs = with python3Packages; [
        pyyaml requests
    ];
}
