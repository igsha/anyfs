{ lib, python3Packages }:

let
  toml = builtins.fromTOML (builtins.readFile ./pyproject.toml);
in python3Packages.buildPythonApplication {
  pname = "anyfs";
  version = toml.project.version;
  pyproject = true;

  src = ./.;

  build-system = with python3Packages; [ setuptools ];
  dependencies = with python3Packages; [ fuse requests sortedcontainers ];

  meta = {
    description = "A fuse-based filesystem";
    homepage = https://github.com/igsha/anyfs;
    license = lib.licenses.mit;
    maintainers = with lib.maintainers; [ igsha ];
    platforms = lib.platforms.linux;
  };
}
