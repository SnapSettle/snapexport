import os
import subprocess
import inkex


class SnapExport(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--path", type=str, default="/tmp/snapexport")
        pars.add_argument("--filename", type=str, default="illustration")
        pars.add_argument("--do_png", type=inkex.Boolean, default=True)
        pars.add_argument("--do_jpg", type=inkex.Boolean, default=True)

        # SVG Sub-arguments directly evaluated
        pars.add_argument("--do_svg_plain", type=inkex.Boolean, default=False)
        pars.add_argument("--do_svg_inkscape", type=inkex.Boolean, default=False)
        pars.add_argument("--do_svg_optimized", type=inkex.Boolean, default=True)

        pars.add_argument("--do_pdf", type=inkex.Boolean, default=True)
        pars.add_argument("--do_eps", type=inkex.Boolean, default=True)

    def effect(self):
        output_dir = os.path.expanduser(self.options.path)
        base_name = self.options.filename
        svg_file = self.options.input_file

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        success_list = []
        error_list = []

        # Process Standard Flat Formats
        standard_formats = {
            "png": self.options.do_png,
            "jpg": self.options.do_jpg,
            "pdf": self.options.do_pdf,
            "eps": self.options.do_eps,
        }

        for ext, checked in standard_formats.items():
            if checked:
                out_path = os.path.join(output_dir, f"{base_name}.{ext}")
                command = ["inkscape", svg_file, "-o", out_path]
                try:
                    subprocess.run(command, check=True, capture_output=True, text=True)
                    success_list.append(f"{base_name}.{ext}")
                except subprocess.CalledProcessError as e:
                    error_msg = e.stderr.strip() if e.stderr else str(e)
                    error_list.append((ext.upper(), error_msg))

        # Process SVG Formats directly based on checkboxes
        svg_variants = []
        if self.options.do_svg_plain:
            svg_variants.append(("svg-plain", "plain"))
        if self.options.do_svg_inkscape:
            svg_variants.append(("svg-inkscape", "inkscape"))
        if self.options.do_svg_optimized:
            svg_variants.append(("scour", "optimized"))

        # Loop through selected SVG variations
        for export_type, suffix in svg_variants:
            target_filename = (
                f"{base_name}.svg"
                if len(svg_variants) == 1
                else f"{base_name}_{suffix}.svg"
            )
            out_path = os.path.join(output_dir, target_filename)
            command = [
                "inkscape",
                svg_file,
                "--export-type",
                export_type,
                "-o",
                out_path,
            ]

            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                success_list.append(target_filename)
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip() if e.stderr else str(e)
                error_list.append((f"SVG-{suffix.upper()}", error_msg))

        # Construct Custom Clean Layout Report
        log_output = []
        divider = "─" * 45

        if success_list:
            log_output.append(f" {divider}")
            log_output.append("  🎉  EXPORT SUCCESSFUL!")
            log_output.append(f" {divider}")
            log_output.append(f"  📊 Total Compiled:  {len(success_list)}")
            log_output.append(f"  📍 Folder:  {output_dir}")
            log_output.append(f" {divider}")
            log_output.append("  📂  GENERATED FILES")
            log_output.append(f" {divider}")
            for idx, file_item in enumerate(success_list, start=1):
                log_output.append(f"    {idx}.  {file_item}")
            log_output.append(f" {divider}")

        if error_list:
            if success_list:
                log_output.append("\n")
            log_output.append(f" {divider}")
            log_output.append("  ⚠️  SOME ERRORS OCCURRED")
            log_output.append(f" {divider}")
            for fmt_lbl, err_desc in error_list:
                short_err = (err_desc[:40] + "...") if len(err_desc) > 40 else err_desc
                log_output.append(f"    ❌ [{fmt_lbl}]: {short_err}")
            log_output.append(f" {divider}")

        if log_output:
            self.msg("\n".join(log_output))


if __name__ == "__main__":
    SnapExport().run()
