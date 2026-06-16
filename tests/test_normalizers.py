import unittest

from kp_normalizer import normalize_identifier_value


class NormalizerTests(unittest.TestCase):
    def test_normalize_identifier_value_formats_excel_numeric_ids(self) -> None:
        self.assertEqual(normalize_identifier_value(169.0), "169")
        self.assertEqual(normalize_identifier_value(1521), "1521")
        self.assertEqual(normalize_identifier_value(" 0169.0 "), "0169.0")
        self.assertEqual(normalize_identifier_value(169.5), "169.5")


if __name__ == "__main__":
    unittest.main()
