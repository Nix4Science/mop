# Mop

A posteriori Nix shells

## Use case

You have a dirty software environment and you want to get Nix shells with the same packages and versions.

## Usage

Describe the different shells, packages, and desired versions in a YAML file:

```yaml
- shell: analysis
  packages:
    - name: python310
      version: "3.10.8"
      with_packages:
      - name: numpy
        version: "1.24.2"
      - name: matplotlib
        version: "3.7.1"
- shell: dev
  packages:
    - name: gcc
      version: "12.3.0"
    - name: cmake
      version: "3.24.3"

```

- `shell` sets the name of the shell

- `packages` is a list of pairs (`name`, `version`)

- for some packages (`python`, `R`, ...), you can use the `with_packages` fields to add some packages (`numpy` and `matplotlib` in the example above)

Then run `mop`:

```bash
mop envs.yaml
```

`mop` will generate a `flake.nix` file that **tries** to match as best as it can the desired environments.

## Notes and Warnings

- `mop` calls [Nixhub](https://nixhub.io) under the hood to retrieve the correct `nixpkgs` commits

- you do want to call a nix formatter on the generated `flake.nix`!!

- for now, the `with_packages` supports fully `python`, and partially `R`

- it might require you to edit the `flake.nix` to fill up some `sha256` or `hash`

