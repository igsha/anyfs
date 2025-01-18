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
      inputsFrom = [ self.packages.x86_64-linux.anyfs ];
      PYTHONDONTWRITEBYTECODE = 1;
    };
  };
}
