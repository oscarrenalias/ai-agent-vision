import unittest

from agents.pricecomparison.price_lookup_tools import s_kaupat_price_lookup


class TestPriceLookupTools(unittest.TestCase):
    """Test cases for the price_lookup_tools module."""

    def test_s_kaupat_price_lookup_with_results(self):
        """Test s_kaupat_price_lookup when results are found."""
        result = s_kaupat_price_lookup.invoke("maito")
        self.assertTrue("maito" in result["message"].lower())

    def test_s_kaupat_price_lookup_no_results(self):
        """Test s_kaupat_price_lookup when no results are found."""
        result = s_kaupat_price_lookup.invoke("unknown_item")
        self.assertFalse("unkown_item" in result)
