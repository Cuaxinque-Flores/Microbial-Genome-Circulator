from pathlib import Path
from typing import List, Optional

from csplotter.genbank import Genbank


class CircosConfig:
    """Circos Config Class"""

    def __init__(
        self,
        ref_gbk: Genbank,
        outdir: Path,
        window_size: int = 5000,
        step_size: int = 2000,
        forward_cds_color: str = "red",
        reverse_cds_color: str = "blue",
        rrna_color: str = "green",
        trna_color: str = "purple",
        gc_content_p_color: str = "black",
        gc_content_n_color: str = "grey",
        gc_skew_p_color: str = "blue",
        gc_skew_n_color: str = "orange",
    ):
        """Constructor"""
        self.ref_gbk = ref_gbk
        self.outdir = outdir
        self.window_size = window_size
        self.step_size = step_size
        self.forward_cds_color = forward_cds_color
        self.reverse_cds_color = reverse_cds_color
        self.rrna_color = rrna_color
        self.trna_color = trna_color
        self.gc_content_p_color = gc_content_p_color
        self.gc_content_n_color = gc_content_n_color
        self.gc_skew_p_color = gc_skew_p_color
        self.gc_skew_n_color = gc_skew_n_color

        self._config_file = outdir / "circos.conf"
        self._ideogram_file = outdir / "ideogram.conf"
        self._ticks_file = outdir / "ticks.conf"
        self._karyotype_file = outdir / "karyotype.txt"
        self._forward_cds_file = outdir / "forward_cds.txt"
        self._reverse_cds_file = outdir / "reverse_cds.txt"
        self._rrna_file = outdir / "rRNA.txt"
        self._trna_file = outdir / "tRNA.txt"
        self._gc_skew_file = outdir / "gc_skew.txt"
        self._gc_content_file = outdir / "gc_content.txt"

        self._r_counter = 1.0
        self._feature_r = 0.05
        self._query_r = 0.05
        self._gc_content_r = 0.15
        self._gc_skew_r = 0.15

    def write_config_file(self, config_outfile: Path) -> Path:
        """Write circos config file"""
        # Circos config
        self._write_karyotype_conf()
        self._write_ideogram_conf()
        self._write_ticks_conf()
        # Feature config
        feature_conf = ""
        feature_conf += self._add_feature(
            self._forward_cds_file, ["CDS"], 1, self.forward_cds_color
        )
        feature_conf += self._add_feature(
            self._reverse_cds_file, ["CDS"], -1, self.reverse_cds_color
        )
        feature_conf += self._add_feature(
            self._rrna_file, ["rRNA"], None, self.rrna_color
        )
        feature_conf += self._add_feature(
            self._trna_file, ["tRNA"], None, self.trna_color
        )
        # GC content & skew config
        gc_content_conf = self._add_gc_content()
        gc_skew_conf = self._add_gc_skew()
        config_contents = self._concat_lines(
            [
                "karyotype = {0}".format(self._karyotype_file),
                "chromosomes_units = 1000000",
                "<<include {0}>>".format(self._ideogram_file),
                "<<include {0}>>".format(self._ticks_file),
                "<plots>",
                feature_conf,
                gc_content_conf,
                gc_skew_conf,
                "</plots>",
                "<image>",
                "<<include image.conf>>",
                "</image>",
                "<<include colors_fonts_patterns.conf>> ",
                "<<include housekeeping.conf>> ",
            ]
        )

        with open(config_outfile, "w") as f:
            f.write(config_contents)

        return self._config_file

    ###########################################################################
    # Karyotype config
    ###########################################################################
    def _write_karyotype_conf(self) -> None:
        genome_length = self.ref_gbk.genome_length
        with open(self._karyotype_file, "w") as f:
            f.write(f"chr - main 1 0 {genome_length} grey")

    ###########################################################################
    # Ideogram config
    ###########################################################################
    def _write_ideogram_conf(self) -> None:
        contents = self._concat_lines(
            [
                "<ideogram>",
                "<spacing>",
                "default = 0.005r",
                "</spacing>",
                "radius           = 0.90r",
                "thickness        = 20p",
                "fill             = yes",
                "stroke_color     = dgrey",
                "stroke_thickness = 2p",
                "show_label       = yes",
                "label_font       = default ",
                "label_radius     = 1r + 75p",
                "label_size       = 30",
                "label_parallel   = yes",
                "</ideogram>",
            ]
        )
        with open(self._ideogram_file, "w") as f:
            f.write(contents)

    ###########################################################################
    # Ticks config
    ###########################################################################
    def _write_ticks_conf(self) -> None:
        contents = self._concat_lines(
            [
                "show_ticks       = yes",
                "show_tick_labels = yes",
                "<ticks>",
                "radius     = 1r",
                "color      = black",
                "thickness  = 2p",
                "multiplier = 1e-6",
                "format     = %d",
                "<tick>",
                "spacing = 5u",
                "size    = 10p",
                "</tick>",
                "<tick>",
                "spacing      = 25u",
                "size         = 15p",
                "show_label   = yes",
                "label_size   = 20p",
                "label_offset = 10p",
                "format       = %d",
                "</tick>",
                "</ticks>",
            ]
        )
        with open(self._ticks_file, "w") as f:
            f.write(contents)

    ###########################################################################
    # Feature(CDS, rRNA, tRNA) config
    ###########################################################################
    def _add_feature(
        self,
        feature_file: Path,
        feature_types: List[str],
        target_strand: Optional[int] = None,
        color: str = "grey",
    ) -> str:
        self._write_feature_file(feature_file, feature_types, target_strand, color)
        contents = self._concat_lines(
            [
                f"##### {'-'.join(feature_types)} Features #####",
                "<plot>",
                "type             = tile",
                "file             = {0}".format(feature_file),
                "r0               = {0}r".format(self._r_counter - self._feature_r),
                "r1               = {0}r".format(self._r_counter),
                "orientation      = out",
                "layers           = 1",
                "margin           = 0.01u",
                "thickness        = 50",
                "padding          = 1",
                "stroke_color     = black",
                "stroke_thickness = 0",
                "layers_overflow  = collapse",
                "</plot>",
            ]
        )
        self._r_counter -= self._feature_r
        return contents

    def _write_feature_file(
        self,
        feature_file: Path,
        feature_types: List[str],
        target_strand: Optional[int],
        color: str,
    ) -> None:
        features = self.ref_gbk.extract_all_features(feature_types, target_strand)
        contents = ""
        for f in features:
            start, end, strand = f.location.start, f.location.end, f.strand
            strand = "+" if strand == 1 else "-"
            contents += f"main {start} {end} {strand} color={color}\n"
        with open(feature_file, "w") as f:
            f.write(contents)

    ###########################################################################
    # GC skew config
    ###########################################################################
    def _add_gc_skew(self) -> str:
        self._r_counter = 0.6 if self._r_counter > 0.6 else self._r_counter
        abs_max_value = self._write_gc_skew_file()
        contents = self._concat_lines(
            [
                "##### GC Skew #####",
                "<plot>",
                "type        = line",
                "file        = {0}".format(self._gc_skew_file),
                "r0          = {0}r".format(self._r_counter - self._gc_skew_r),
                "r1          = {0}r".format(self._r_counter),
                "min         = -{0}".format(abs_max_value),
                "max         = {0}".format(abs_max_value),
                "thickness   = 0",
                "orientation = out",
                "</plot>",
            ]
        )
        self._r_counter -= self._gc_skew_r
        return contents

    def _write_gc_skew_file(self) -> float:
        gc_skew_values = self.ref_gbk.gc_skew(self.window_size, self.step_size)
        contents = ""
        for i, value in enumerate(gc_skew_values):
            pos = i * self.step_size
            color = self.gc_skew_p_color if value > 0 else self.gc_skew_n_color
            contents += f"main {pos} {pos} {value} fill_color={color}\n"
        with open(self._gc_skew_file, "w") as f:
            f.write(contents)
        return max(abs(v) for v in gc_skew_values)

    ###########################################################################
    # GC content config
    ###########################################################################
    def _add_gc_content(self) -> str:
        self._r_counter = 0.6 if self._r_counter > 0.6 else self._r_counter
        abs_max_value = self._write_gc_content_file()
        contents = self._concat_lines(
            [
                "##### GC Content #####",
                "<plot>",
                "type        = line",
                "file        = {0}".format(self._gc_content_file),
                "r0          = {0}r".format(self._r_counter - self._gc_content_r),
                "r1          = {0}r".format(self._r_counter),
                "min         = -{0}".format(abs_max_value),
                "max         = {0}".format(abs_max_value),
                "thickness   = 0",
                "orientation = out",
                "</plot>",
            ]
        )
        self._r_counter -= self._gc_content_r
        return contents

    def _write_gc_content_file(self) -> float:
        gc_content_values = self.ref_gbk.gc_content(self.window_size, self.step_size)
        gc_content_values = [v - self.ref_gbk.average_gc for v in gc_content_values]
        contents = ""
        for i, value in enumerate(gc_content_values):
            pos = i * self.step_size
            color = self.gc_content_p_color if value > 0 else self.gc_content_n_color
            contents += f"main {pos} {pos} {value} fill_color={color}\n"
        with open(self._gc_content_file, "w") as f:
            f.write(contents)
        return max(abs(v) for v in gc_content_values)

    def _concat_lines(self, lines: List[str]) -> str:
        """Concatenate lines

        Args:
            lines (List[str]): Target lines

        Returns:
            str: Concatenated lines string
        """
        return "\n".join(lines) + "\n"
