class Shell:
    def __init__(self, name):
        self.name = name
        self.pkgs = []

    def set_overlay_names(self):
        for pkg in self.pkgs:
            if pkg.with_packages:
                pkg.overlay_name = f"overlay_shell_{self.name}_package_{pkg.name}"

    def generate_imports(self):
        return "\n".join([f"\t\tpkgs_shell_{self.name}_{pkg.name} = import inputs.{pkg.flake_input} {{ inherit system; overlays = [ {pkg.overlay_name} ]; }};" for pkg in self.pkgs])

    def generate_flake_inputs(self):
        return list(map(lambda x: x.generate_flake_input(), self.pkgs))

    def generate_overlays(self):
        return "\n".join(map(lambda x: x.generate_overlay(), self.pkgs))

    def generate_shell(self):
        pkgs_calls = " ".join(map(lambda x: x.generate_call(f"pkgs_shell_{self.name}_{x.name}"), self.pkgs))
        return f"\t\t\t{self.name} = pkgs.mkShell {{ packages = [ {pkgs_calls} ]; }};"


class Package:
    def __init__(self, name, version, derivation=None, with_packages=None):
        self.name = name
        self.derivation = derivation if derivation else name
        # TODO: python310: append version to derivation
        self.version = version
        self.with_packages = with_packages
        self.flake_input = f"{self.derivation}_{self.version.replace('.', '_')}"
        self.nixpkgs_commit = None
        self.overlay_name = ""

    def generate_flake_input(self):
        if self.nixpkgs_commit:
            return f"\t\t{self.flake_input}.url = \"github:nixos/nixpkgs?rev={self.nixpkgs_commit}\";"
        return ""

    def generate_overlay_python(self):
        packages = []
        for with_pkg in self.with_packages:
            package = with_pkg["name"]
            version = with_pkg["version"]
            pkg_str = f"""
{package} = pyprev.{package}.overrideAttrs (finalAttrs: prevAttrs: {{
    version = "{version}";
    src = pyprev.fetchPypi {{
        pname = prevAttrs.pname;
        version = "{version}";
        extension = "tar.gz";
        hash = "";
      }};
}});"""
            packages.append(pkg_str)

        pkgs_string = "\n".join(packages)
        return f"""
{self.overlay_name} = final: prev: {{
    {self.derivation} = prev.{self.derivation}.override {{
        packageOverrides = pyfinal: pyprev: {{
{pkgs_string}
        }};
    }};
}};"""

    def generate_overlay_R(self):
        return f"\t\t{self.overlay_name} = final: prev: {{ }};"

    def generate_overlay(self):
        if self.with_packages is None:
            return ""
        if "python" in self.name:
            return self.generate_overlay_python()
        elif self.name == "R" or self.name == "r":
            return self.generate_overlay_R()
        else:
            assert False, "unimplemented"

    def generate_call_python(self, pkgs):
        return f"({pkgs}.{self.derivation}.withPackages (ps: with ps; [ {' '.join(map(lambda x: x['name'], self.with_packages))} ])"

    def generate_call_R(self, pkgs):
        return f"({pkgs}.rWrapper.override {{ packages = with {pkgs}.rPackages; [ {' '.join(map(lambda x: x['name'], self.with_packages))} ];}})"

    def generate_call(self, pkgs):
        if self.with_packages is None:
            return f"{pkgs}.{self.derivation}"

        if "python" in self.name:
            return self.generate_call_python(pkgs)
        elif self.name == "R" or self.name == "r":
            return self.generate_call_R(pkgs)
        else:
            assert False, "unimplemented"
