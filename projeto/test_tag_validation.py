import unittest
from projeto.api import carregar_catalogo
from projeto.image_processing import PIDImageProcessor


class TestTagValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogo = carregar_catalogo()

    def _classify_text(self, text, dummy_conf=0.95):
        cleaned = PIDImageProcessor._clean_ocr_text(text)
        compact = PIDImageProcessor._normalize_tag(text)

        if compact in self.catalogo:
            ref = self.catalogo[compact]
            return {
                "tag": compact,
                "status": "Identificado",
                "tipo": ref["tipo"],
                "classe": ref["classe"],
            }

        if PIDImageProcessor._is_possible_technical_tag(cleaned):
            return {
                "tag": PIDImageProcessor._normalize_tag(cleaned),
                "status": "Possível TAG",
                "tipo": "Não cadastrado",
                "classe": "Não cadastrado",
            }

        return None

    def test_identificado_catalog_tags(self):
        """TAGs presentes no catálogo devem ser classificadas como Identificado."""
        catalog_samples = ["FO", "FC", "FL", "LT210", "FV210", "M210", "FL/DO", "FL/DC"]
        for sample in catalog_samples:
            res = self._classify_text(sample)
            self.assertIsNotNone(res, f"Esperava detecção para {sample}")
            self.assertEqual(res["status"], "Identificado", f"{sample} deveria ser Identificado")
            self.assertNotEqual(res["tipo"], "Não cadastrado")
            self.assertNotEqual(res["classe"], "Não cadastrado")

    def test_possivel_tag_generic_technical(self):
        """TAGs tecnicamente válidas fora do catálogo devem ser Possível TAG."""
        generic_samples = [
            "PT-0004", "PSL-0003", "PSLL-0014", "LSH-0002", "V-001",
            "ZSH1", "TC", "PC", "FC", "FE", "HV", "ASC", "ASV", "CSO", "KOD"
        ]
        for sample in generic_samples:
            res = self._classify_text(sample)
            self.assertIsNotNone(res, f"Esperava detecção para {sample}")
            self.assertIn(res["status"], ["Identificado", "Possível TAG"])
            if sample not in self.catalogo:
                self.assertEqual(res["status"], "Possível TAG")
                self.assertEqual(res["tipo"], "Não cadastrado")
                self.assertEqual(res["classe"], "Não cadastrado")

    def test_standalone_legitimate_vs_fragment(self):
        """Abreviações funcionais autônomas são aceitas; prefixos de malha incompletos isolados são suprimidos."""
        # Abreviações autônomas legítimas
        for tag in ["TC", "FC", "PC", "LC", "FE", "HV", "ASC", "ASV", "KOD", "CSO"]:
            self.assertTrue(tag in PIDImageProcessor.STANDALONE_TECHNICAL_TAGS, f"{tag} deve ser autônoma")
        
        # Prefixos de malha que exigem número (não devem estar em STANDALONE_TECHNICAL_TAGS)
        for loop_pfx in ["PSLL", "LSL", "LSHL", "LAH", "LAL", "PAL", "PAH", "PT"]:
            self.assertNotIn(loop_pfx, PIDImageProcessor.STANDALONE_TECHNICAL_TAGS, f"{loop_pfx} é de malha e exige número")

    def test_pipe_codes_and_noise_rejected(self):
        """Códigos de tubulação, ruídos com pontuação e dimensões NÃO devem virar TAG."""
        rejected_samples = [
            '3"-Po96-15A-V', '36"_PO12_154-V', '900#', '3/4"', 'ILo]I', 'P096', 'QO16C', 'IL8I',
            "NOTE", "WATER", "PUMP", "TANK", "SAFE", "VENT", "COMPRESSOR", "12345", "A", "1"
        ]
        for sample in rejected_samples:
            res = self._classify_text(sample)
            self.assertIsNone(res, f"'{sample}' NÃO deveria ser promovido a TAG (retornou: {res})")

    def test_b8_contextual_normalization(self):
        """Correção contextual B/8 atua apenas em loops de 4 dígitos e não corrompe tags reais com 8."""
        # Loops de 4 dígitos corrigidos
        self.assertEqual(PIDImageProcessor._clean_ocr_text("PSLL-00168"), "PSLL-0016B")
        self.assertEqual(PIDImageProcessor._clean_ocr_text("PSL-00178"), "PSL-0017B")

        # Tags com 8 genuíno NÃO são corrompidas
        self.assertEqual(PIDImageProcessor._clean_ocr_text("LT218"), "LT218")
        self.assertEqual(PIDImageProcessor._clean_ocr_text("V-108"), "V-108")
        self.assertEqual(PIDImageProcessor._clean_ocr_text("PT-208"), "PT-208")

    def test_spatial_recomposition_valid_pairs(self):
        """Fragmentos alinhados verticalmente (ISA bubble) devem ser recompostos como PREFIXO-NÚMERO."""
        raw_items = [
            {"text": "PT", "norm": "PT", "prob": 0.98, "bbox": {"x": 950, "y": 150, "width": 30, "height": 20}},
            {"text": "0004", "norm": "0004", "prob": 1.00, "bbox": {"x": 948, "y": 172, "width": 40, "height": 20}},
            {"text": "PSLL", "norm": "PSLL", "prob": 1.00, "bbox": {"x": 1500, "y": 140, "width": 45, "height": 20}},
            {"text": "00168", "norm": "00168", "prob": 0.99, "bbox": {"x": 1498, "y": 162, "width": 40, "height": 20}},
        ]
        recomposed = PIDImageProcessor._recompose_split_tags(raw_items, tag_catalog=self.catalogo)
        tags_found = [d["tag"] for d in recomposed]

        self.assertIn("PT-0004", tags_found, "Esperava PT-0004 recomposto")
        self.assertIn("PSLL-0016B", tags_found, "Esperava PSLL-0016B corrigido e recomposto")


if __name__ == "__main__":
    unittest.main(verbosity=2)
