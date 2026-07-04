{
  description = "Inkscape SnapExport Extension Development Environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      treefmt-nix,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Setup treefmt configuration for simple formatting
        treefmtConfig = treefmt-nix.lib.evalModule pkgs {
          projectRootFile = "flake.nix";

          programs.black.enable = true; # Formatter for Python (.py)
          programs.nixfmt.enable = true;

          settings.formatter = {
            xmlformat = {
              command = "${pkgs.xmlstarlet}/bin/xmlstarlet";
              options = [
                "fo"
                "-s"
                "4"
              ];
              includes = [ "*.inx" ];
            };
          };
        };
      in
      {
        # Expose the formatter runner directly via `nix fmt`
        formatter = treefmtConfig.config.build.wrapper;

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python core environment with Inkscape Extension dependency
            (python3.withPackages (
              ps: with ps; [
                inkex
              ]
            ))

            # LSP Code completion & Analysis Support
            pyright

            # XML Formatter
            xmlstarlet

            # Formatting engine wrapper
            treefmtConfig.config.build.wrapper
          ];

          shellHook = ''
            echo "================================================="
            echo "🎉 SnapExport Dev Environment Loaded"
            echo "💻 LSP Support: 'pyright' is ready"
            echo "🎨 Formatter: Run 'nix fmt' to tidy code and XML files"
            echo "================================================="
          '';
        };
      }
    );
}
