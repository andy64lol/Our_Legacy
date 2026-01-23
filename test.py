import unittest
from unittest.mock import MagicMock, patch
import os
import json
import io
import contextlib
import main

class TestOurLegacy(unittest.TestCase):
    def setUp(self):
        # Disable colors and suppress stdout for cleaner test runs
        main.COLORS_ENABLED = False
        self.suppress_output = contextlib.redirect_stdout(io.StringIO())
        self.suppress_output.__enter__()

    def tearDown(self):
        self.suppress_output.__exit__(None, None, None)

    def test_colors_toggle(self):
        main.COLORS_ENABLED = True
        self.assertEqual(main.Colors._color(main.Colors.RED), main.Colors.RED)
        main.COLORS_ENABLED = False
        self.assertEqual(main.Colors._color(main.Colors.RED), "")

    def test_progress_bars(self):
        # Test standard progress bar
        bar = main.create_progress_bar(50, 100, width=10)
        self.assertIn("50.0%", bar)
        
        # Test boss HP bar
        boss_bar = main.create_boss_hp_bar(500, 1000, width=20)
        self.assertIn("BOSS HP", boss_bar)
        self.assertIn("50.0%", boss_bar)
        
        # Test edge case
        empty_bar = main.create_progress_bar(0, 0)
        self.assertIn("[", empty_bar)

    def test_rarity_logic(self):
        self.assertEqual(main.get_rarity_color("legendary"), main.Colors.LEGENDARY)
        self.assertEqual(main.get_rarity_color("unknown"), main.Colors.WHITE)
        
        formatted = main.format_item_name("Excalibur", "epic")
        self.assertIn("Excalibur", formatted)

    @patch('builtins.input', side_effect=['yes'])
    @patch('main.clear_screen')
    def test_ask_valid(self, mock_clear, mock_input):
        result = main.ask("Confirm?", valid_choices=['yes', 'no'])
        self.assertEqual(result, 'yes')

    def test_scripting_engine_logic(self):
        # Test engine behavior when Node is unavailable
        with patch('main._check_node_available', return_value=False):
            engine = main.ScriptingEngine()
            self.assertFalse(engine.scripting_enabled)
            
        # Test engine behavior when Node is available but fails test
        with patch('main._check_node_available', return_value=True):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=1)
                engine = main.ScriptingEngine()
                self.assertFalse(engine.scripting_enabled)

if __name__ == '__main__':
    unittest.main()
