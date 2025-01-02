{ lib, python3Packages }:

python3Packages.buildPythonApplication {
  pname = "anyfs";
  version = "0.0.1";
  pyproject = true;

  src = ./.;

  build-system = with python3Packages; [ setuptools ];
  dependencies = with python3Packages; [ fuse ];

  meta = {
    description = "A fuse-based filesystem";
    homepage = https://github.com/igsha/anyfs;
    license = lib.licenses.mit;
    maintainers = with lib.maintainers; [ igsha ];
    platforms = lib.platforms.linux;
  };
}
