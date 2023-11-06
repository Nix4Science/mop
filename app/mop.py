import yaml
import sys
import logging
import requests
import argparse
from itertools import chain
from string import Template

from package import Package, Shell

logging.basicConfig(level=logging.WARNING)

FLAKE_TEMPLATE = """
{
    inputs = {
        nixpkgs.url = "github:nixos/nixpkgs/$nixpkgs_tag";
$inputs
    };

    outputs = {self, nixpkgs, ...}@inputs:
    let
        system = "$nix_system";
        pkgs = nixpkgs.legacyPackages.${system};
$overlays
$imports
    in
    {
        devShells.${system} = {
$shells
        };
    };
}
"""

def read_yaml(filename):
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)
    return data

def ask_nixhub_io(package):
    return "01"
    resp = requests.get(f"https://www.nixhub.io/packages/{package.derivation}?_data=routes/_nixhub.packages.$pkg._index")
    resp_dict = resp.json()
    logging.info(f"GET DATA: {resp_dict}")
    releases = resp_dict["releases"]
    for release in releases:
        if release["version"] == package.version:
            last_update = release["last_updated"]
            for x in release["platforms"]:
                if x["date"] == last_update:
                    return x["commit_hash"]
    logging.warning(f"No nixpkgs commit found for version '{package.version}' of '{package.name}'")
    return None

def main():
    parser = argparse.ArgumentParser(description="Generate Nix shells with desired package versions")
    parser.add_argument("--output", "-o", type=str, default="flake.nix", help="file to store the generated flake.nix")
    parser.add_argument("description", type=str, help="YAML file containing the description of the shells")
    parser.add_argument("--nixpkgs-tag", type=str, default="23.05", help="tag for the default import of nixpkgs (default: 23.05)")
    parser.add_argument("--system", type=str, default="x86_64-linux", help="system (default: x86_64-linux)")
    parser.add_argument("--verbose", action="store_true", help="behind the scene access")

    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    filename = args.description
    logging.info(f"Filename: {filename}")
    data = read_yaml(filename)
    logging.info(f"YAML data: {data}")
    shells = []
    for shell_data in data:
        shell = Shell(shell_data["shell"])
        for package in shell_data["packages"]:
            logging.info(f"package: {package}")
            pkg = Package(**package)
            logging.info(f"Asking for version '{pkg.version}' of {pkg.name}")
            pkg.nixpkgs_commit = ask_nixhub_io(pkg)
            shell.pkgs.append(pkg)
        shell.set_overlay_names()
        shells.append(shell)


    sub_data = {
        "inputs": "\n".join(list(set(chain.from_iterable(map(lambda x: x.generate_flake_inputs(), shells))))),
        "nix_system": args.system,
        "overlays": "\n".join(map(lambda x: x.generate_overlays(), shells)),
        "imports": "\n".join(map(lambda x: x.generate_imports(), shells)),
        "shells": "\n".join(map(lambda x: x.generate_shell(), shells)),
        "nixpkgs_tag": args.nixpkgs_tag
    }

    template_flake = Template(FLAKE_TEMPLATE)
    flake = template_flake.safe_substitute(sub_data)

    with open(args.output, "w") as flake_file:
        flake_file.write(flake)
    logging.info(f"Flake written at '{args.output}'")

    return 0

if __name__ == "__main__":
    main()
