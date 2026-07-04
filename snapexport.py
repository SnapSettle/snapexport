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
        info_notes = []

        # Process Standard Formats (PNG, PDF, EPS)
        standard_formats = {
            "png": self.options.do_png,
            "pdf": self.options.do_pdf,
            "eps": self.options.do_eps,
        }

        for ext, checked in standard_formats.items():
            if checked:
                out_path = os.path.join(output_dir, f"{base_name}.{ext}")
                command = ["inkscape", svg_file, "-o", out_path]
                try:
                    subprocess.run(command, check=True, capture_output=True, text=True)
                    if os.path.exists(out_path):
                        success_list.append(f"{base_name}.{ext}")
                except subprocess.CalledProcessError:
                    pass

        # Process JPEG natively
        if self.options.do_jpg:
            jpg_path = os.path.join(output_dir, f"{base_name}.jpg")
            command = [
                "inkscape",
                svg_file,
                "--export-background=ffffff",
                "--export-type=jpg",
                "-o",
                jpg_path,
            ]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                if os.path.exists(jpg_path):
                    success_list.append(f"{base_name}.jpg")
                else:
                    raise FileNotFoundError
            except (subprocess.CalledProcessError, FileNotFoundError):
                info_notes.append("⚠️  JPEG File Skipped:")
                info_notes.append("   Your system is missing a conversion tool (ImageMagick).")
                info_notes.append("   👉 Fix: Use File -> Export... -> JPG inside Inkscape,")
                info_notes.append("           or convert your generated PNG into a JPEG.")

        # Process SVG Variants natively
        svg_variants = []
        if self.options.do_svg_plain:
            svg_variants.append(("org.inkscape.output.svg.plain", "plain"))
        if self.options.do_svg_inkscape:
            svg_variants.append((None, "inkscape"))
        if self.options.do_svg_optimized:
            svg_variants.append(("org.inkscape.output.scour.inkscape", "optimized"))

        use_suffix = len(svg_variants) > 1

        for extension_id, suffix in svg_variants:
            target_filename = f"{base_name}_{suffix}.svg" if use_suffix else f"{base_name}.svg"
            out_path = os.path.join(output_dir, target_filename)

            command = ["inkscape", svg_file, "--export-type=svg", "-o", out_path]
            if extension_id:
                command.append(f"--export-extension={extension_id}")

            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                if os.path.exists(out_path):
                    success_list.append(target_filename)
                else:
                    raise FileNotFoundError
            except (subprocess.CalledProcessError, FileNotFoundError):
                if suffix == "optimized":
                    info_notes.append("⚠️  Optimized SVG Skipped:")
                    info_notes.append("   The 'Scour' code-cleaner utility is missing.")
                    info_notes.append("   👉 Fix 1: Export as 'Plain SVG' instead.")
                    info_notes.append("   👉 Fix 2: Install the 'Scour' utility in your system.")

        # Construct Clean Layout Dialog Report
        log_output = []
        divider = "─" * 45

        if success_list:
            log_output.append(f" {divider}")
            log_output.append("  🎉  EXPORT TASK COMPLETED")
            log_output.append(f" {divider}")
            log_output.append(f"  📊 Total Saved:  {len(success_list)}")
            log_output.append(f"  📍 Folder:  {output_dir}")
            log_output.append(f" {divider}")
            log_output.append("  📂  GENERATED FILES")
            log_output.append(f" {divider}")
            for idx, file_item in enumerate(success_list, start=1):
                log_output.append(f"    {idx}.  {file_item}")
            log_output.append(f" {divider}")

        if info_notes:
            if success_list:
                log_output.append("\n")
            log_output.append(f" {divider}")
            log_output.append("  💡  FIX MISSING FORMATS (PICK ONE FOR EACH)")
            log_output.append(f" {divider}")
            for note in info_notes:
                log_output.append(f"  {note}")
            log_output.append(f" {divider}")

        if log_output:
            self.msg("\n".join(log_output))


if __name__ == "__main__":
    SnapExport().run()