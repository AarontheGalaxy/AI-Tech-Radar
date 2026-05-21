import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import main

class TestMainRefactor(unittest.TestCase):

    @patch('main.load_dotenv')
    @patch('main.fetch_all')
    @patch('main.process_and_summarize')
    @patch('main.save_report')
    @patch('main.launch_interactive')
    @patch('builtins.input', side_effect=['y'])
    @patch('main.time.time', side_effect=[100, 105])
    def test_main_interactive_yes(self, mock_time, mock_input, mock_launch, mock_save, mock_process, mock_fetch, mock_dotenv):
        # Setup
        mock_fetch.return_value = [{'title': 'item1'}]
        mock_process.return_value = {'one_liner': 'Summary', 'top_20': []}
        
        # Execute
        main.main()
        
        # Verify
        mock_fetch.assert_called_once()
        mock_process.assert_called_once_with([{'title': 'item1'}])
        mock_save.assert_called_once()
        mock_launch.assert_called_once_with(mock_process.return_value, [{'title': 'item1'}])

    @patch('main.load_dotenv')
    @patch('main.fetch_all')
    @patch('main.process_and_summarize')
    @patch('main.save_report')
    @patch('main.launch_interactive')
    @patch('builtins.input', side_effect=['n'])
    @patch('builtins.print')
    @patch('main.time.time', side_effect=[100, 105])
    def test_main_interactive_no(self, mock_time, mock_print, mock_input, mock_launch, mock_save, mock_process, mock_fetch, mock_dotenv):
        # Setup
        mock_fetch.return_value = [{'title': 'item1'}]
        mock_process.return_value = {'one_liner': 'Summary', 'top_20': []}
        
        # Execute
        main.main()
        
        # Verify
        mock_fetch.assert_called_once()
        mock_process.assert_called_once_with([{'title': 'item1'}])
        mock_save.assert_called_once()
        mock_launch.assert_not_called()
        mock_print.assert_any_call('\nSummary')

    def test_display_results_removed(self):
        self.assertFalse(has_allattr(main, 'display_results'), "display_results should be removed")

def has_allattr(obj, name):
    return hasattr(obj, name)

if __name__ == '__main__':
    unittest.main()
