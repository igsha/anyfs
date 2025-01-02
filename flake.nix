{
  description = "A fuse-based filesystem";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }: let
    pkgs = nixpkgs.legacyPackages.x86_64-linux;
  in {
    packages.x86_64-linux = rec {
      anyfs = pkgs.callPackage ./default.nix { };
      default = anyfs;
    };
    devShells.x86_64-linux.default = with pkgs; mkShell {
      nativeBuildInputs = [
        (python3.withPackages (ps: with ps; [ fuse ]))
      ];
      PYTHONDONTWRITEBYTECODE = 1;
    };
  };
}
