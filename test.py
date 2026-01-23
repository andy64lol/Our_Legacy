import unittest
from unittest.mock import MagicMock, patch
import os
import json
import main

class TestOurLegacy(unittest.TestCase):
    def setUp(self):
        main.COLORS_ENABLED = False

    def test_colors_toggle(self):
        main.COLORS_ENABLED = True
        self.assertEqual(main.Colors._color(main.Colors.RED), main.Colors.RED)
        main.COLORS_ENABLED = False
        self.assertEqual(main.Colors._color(main.Colors.RED), "")

    def test_progress_bar(self):
        bar = main.create_progress_bar(50, 100, width=10)
        self.assertIn("50.0%", bar)
        empty_bar = main.create_progress_bar(0, 0)
        self.assertIn("[", empty_bar)

    def test_rarity_colors(self):
        self.assertEqual(main.get_rarity_color("legendary"), main.Colors.LEGENDARY)
        self.assertEqual(main.get_rarity_color("unknown"), main.Colors.WHITE)

    @patch('builtins.input', side_effect=['yes'])
    @patch('main.clear_screen')
    def test_ask_valid(self, mock_clear, mock_input):
        result = main.ask("Confirm?", valid_choices=['yes', 'no'])
        self.assertEqual(result, 'yes')

    def test_scripting_engine_init(self):
        with patch('main._check_node_available', return_value=False):
            engine = main.ScriptingEngine()
            self.assertFalse(engine.scripting_enabled)

if __name__ == '__main__':
    unittest.main()
