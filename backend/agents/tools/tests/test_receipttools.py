import unittest

from agents.tools.receipttools import is_correct_item_type


class TestReceiptTools(unittest.TestCase):
    """Test cases for the receipttools module."""

    def test_is_correct_item_type_with_matching_level1(self):
        """Test is_correct_item_type when level_1 matches the item_type."""
        item = {"item_category": {"level_1": "Food", "level_2": "Grains & Pasta", "level_3": "Rice"}}
        self.assertTrue(is_correct_item_type(item, "food"))
        self.assertTrue(is_correct_item_type(item, "FOOD"))  # Case insensitive
        self.assertTrue(is_correct_item_type(item, "Food"))  # Case insensitive

    def test_is_correct_item_type_with_matching_level2(self):
        """Test is_correct_item_type when level_2 matches the item_type."""
        item = {"item_category": {"level_1": "Food", "level_2": "Grains & Pasta", "level_3": "Rice"}}
        self.assertTrue(is_correct_item_type(item, "pasta"))
        self.assertTrue(is_correct_item_type(item, "PASTA"))  # Case insensitive
        self.assertTrue(is_correct_item_type(item, "Pasta"))  # Case insensitive

    def test_is_correct_item_type_with_matching_level3(self):
        """Test is_correct_item_type when level_3 matches the item_type."""
        item = {"item_category": {"level_1": "Food", "level_2": "Grains & Pasta", "level_3": "Rice"}}
        self.assertTrue(is_correct_item_type(item, "rice"))
        self.assertTrue(is_correct_item_type(item, "RICE"))  # Case insensitive
        self.assertTrue(is_correct_item_type(item, "Rice"))  # Case insensitive

    def test_is_correct_item_type_with_no_match(self):
        """Test is_correct_item_type when there's no match."""
        item = {"item_category": {"level_1": "Food", "level_2": "Grains & Pasta", "level_3": "Rice"}}
        self.assertFalse(is_correct_item_type(item, "vegetable"))
        self.assertFalse(is_correct_item_type(item, "dairy"))
        self.assertFalse(is_correct_item_type(item, "fish"))

    def test_is_correct_item_type_with_missing_levels(self):
        """Test is_correct_item_type with missing category levels."""
        # Only level_1 defined
        item = {"item_category": {"level_1": "Food"}}
        self.assertTrue(is_correct_item_type(item, "food"))
        self.assertFalse(is_correct_item_type(item, "meat"))

        # Only level_1 and level_2 defined
        item = {
            "item_category": {
                "level_1": "Food",
                "level_2": "Grains & Pasta",
            }
        }
        self.assertTrue(is_correct_item_type(item, "food"))
        self.assertTrue(is_correct_item_type(item, "pasta"))
        self.assertFalse(is_correct_item_type(item, "chicken"))

    def test_is_correct_item_type_with_none_category(self):
        """Test is_correct_item_type when item_category is None."""
        item = {"item_category": None}
        self.assertFalse(is_correct_item_type(item, "food"))

    def test_is_correct_item_type_with_non_dict_category(self):
        """Test is_correct_item_type when item_category is not a dict."""
        item = {"item_category": "food"}
        self.assertFalse(is_correct_item_type(item, "food"))


if __name__ == "__main__":
    unittest.main()
