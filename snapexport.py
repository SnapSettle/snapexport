import os
import subprocess
import shutil
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

        # Process Base Formats (PNG, PDF, EPS)
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

        # Process Native Inkscape SVG (Direct file copy of your project file)
        if self.options.do_svg_inkscape:
            inkscape_svg_name = f"{base_name}_inkscape.svg" if (self.options.do_svg_plain or self.options.do_svg_optimized) else f"{base_name}.svg"
            inkscape_svg_path = os.path.join(output_dir, inkscape_svg_name)
            try:
                shutil.copy2(svg_file, inkscape_svg_path)
                success_list.append(inkscape_svg_name)
            except Exception:
                pass

        # Process Plain SVG (Inkscape can reliably clean metadata natively)
        plain_svg_name = f"{base_name}_plain.svg" if (self.options.do_svg_inkscape or self.options.do_svg_optimized) else f"{base_name}.svg"
        plain_svg_path = os.path.join(output_dir, plain_svg_name)
        
        # We always build an intermediate plain vector if an optimized one is requested to feed into Tier 2 scour later
        if self.options.do_svg_plain or self.options.do_svg_optimized:
            command = ["inkscape", svg_file, "--export-type=svg", "--export-extension=org.inkscape.output.svg.plain", "-o", plain_svg_path]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                if os.path.exists(plain_svg_path) and self.options.do_svg_plain:
                    success_list.append(plain_svg_name)
            except subprocess.CalledProcessError:
                pass

        # Process Optimized SVG (Tier 1: Native Extension -> Tier 2: Direct Command)
        if self.options.do_svg_optimized:
            opt_svg_name = f"{base_name}_optimized.svg" if (self.options.do_svg_plain or self.options.do_svg_inkscape) else f"{base_name}.svg"
            opt_svg_path = os.path.join(output_dir, opt_svg_name)
            opt_success = False

            # Tier 1: Try Native Inkscape Optimized Extension Channel
            command = ["inkscape", svg_file, "--export-type=svg", "--export-extension=org.inkscape.output.scour.inkscape", "-o", opt_svg_path]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                if os.path.exists(opt_svg_path):
                    success_list.append(opt_svg_name)
                    opt_success = True
            except subprocess.CalledProcessError:
                pass

            # Tier 2: If Tier 1 skipped, bypass Sandbox and try calling the system 'scour' directly
            if not opt_success:
                if os.path.exists(plain_svg_path) and shutil.which("scour"):
                    scour_cmd = ["scour", "-i", plain_svg_path, "-o", opt_svg_path, "--enable-viewboxing"]
                    try:
                        subprocess.run(scour_cmd, check=True, capture_output=True, text=True)
                        if os.path.exists(opt_svg_path):
                            success_list.append(opt_svg_name)
                            opt_success = True
                    except subprocess.CalledProcessError:
                        pass

            # Tier 3: Notify the user if both methods completely failed
            if not opt_success:
                info_notes.append("⚠️  Optimized SVG Skipped:")
                info_notes.append("   The 'Scour' code-cleaner utility is missing or cannot be reached.")
                info_notes.append("   👉 Fix: Export as 'Plain SVG' or make sure 'scour' is accessible.")

            # Housekeeping: Remove intermediate vector file if plain wasn't requested by the user interface
            if not self.options.do_svg_plain and os.path.exists(plain_svg_path):
                try:
                    os.remove(plain_svg_path)
                except OSError:
                    pass

        # Process JPEG (Tier 1: Native Export -> Tier 2: ImageMagick Conversion)
        if self.options.do_jpg:
            jpg_path = os.path.join(output_dir, f"{base_name}.jpg")
            jpg_success = False

            # Tier 1: Try Native Inkscape JPG Render Engine
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
                    jpg_success = True
            except subprocess.CalledProcessError:
                pass

            # Tier 2: If Tier 1 skipped, bypass Sandbox and convert using direct ImageMagick calls
            if not jpg_success:
                png_source = os.path.join(output_dir, f"{base_name}.png")
                temp_png_created = False

                # Ensure we have a high quality PNG to compress from
                if not os.path.exists(png_source):
                    command = ["inkscape", svg_file, "--export-background=ffffff", "-o", png_source]
                    try:
                        subprocess.run(command, check=True, capture_output=True, text=True)
                        temp_png_created = os.path.exists(png_source)
                    except subprocess.CalledProcessError:
                        pass

                # Locate active system binary variant name
                im_binary = "magick" if shutil.which("magick") else ("convert" if shutil.which("convert") else None)

                if os.path.exists(png_source) and im_binary:
                    img_cmd = [im_binary, png_source, "-background", "white", "-alpha", "remove", jpg_path]
                    try:
                        subprocess.run(img_cmd, check=True, capture_output=True, text=True)
                        if os.path.exists(jpg_path):
                            success_list.append(f"{base_name}.jpg")
                            jpg_success = True
                    except subprocess.CalledProcessError:
                        pass

                # Housekeeping: Remove the temporary raster asset if it wasn't requested by user options
                if temp_png_created and os.path.exists(png_source):
                    try:
                        os.remove(png_source)
                    except OSError:
                        pass

            # Tier 3: Warn the user if both execution channels failed to build a file
            if not jpg_success:
                info_notes.append("⚠️  JPEG File Skipped:")
                info_notes.append("   Your system is missing a conversion tool (ImageMagick).")
                info_notes.append("   👉 Fix: Use File -> Export... -> JPG inside Inkscape,")
                info_notes.append("           or convert your generated PNG into a JPEG.")

        # 6. Construct Clean Layout Dialog Report
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