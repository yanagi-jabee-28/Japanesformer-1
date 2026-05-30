# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, MagicMock
import io
import sys
from japanesformer.cli import parse_args, main

class TestCli(unittest.TestCase):
    """
    japanesformer.cli モジュールに関する単体テスト
    """

    def test_parse_args_defaults(self):
        """
        デフォルト引数が正しく解析されることを検証します。
        """
        args = parse_args(["しんかんせんがはやい"])
        self.assertEqual(args.text, "しんかんせんがはやい")
        self.assertEqual(args.shift, 1)
        self.assertFalse(args.decrypt)
        self.assertFalse(args.no_wave)

    def test_parse_args_custom(self):
        """
        カスタムオプションが正しく解析されることを検証します。
        """
        args = parse_args(["テスト", "-s", "5", "-d", "--no-wave"])
        self.assertEqual(args.text, "テスト")
        self.assertEqual(args.shift, 5)
        self.assertTrue(args.decrypt)
        self.assertTrue(args.no_wave)

    @patch("sys.exit")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_encrypt(self, mock_stdout, mock_exit):
        """
        main 関数が暗号化を正しく実行し、標準出力へ出力することを検証します。
        """
        test_args = ["japanesformer", "しんかんせんがはやい", "-s", "1"]
        with patch.object(sys, "argv", test_args):
            main()
            
        self.assertEqual(mock_stdout.getvalue().strip(), "ちんたんへんぱがばり")
        mock_exit.assert_called_once_with(0)

    @patch("sys.exit")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_decrypt(self, mock_stdout, mock_exit):
        """
        main 関数が復号化を正しく実行し、標準出力へ出力することを検証します。
        """
        test_args = ["japanesformer", "ちんたんへんぱがばり", "-s", "1", "-d"]
        with patch.object(sys, "argv", test_args):
            main()
            
        self.assertEqual(mock_stdout.getvalue().strip(), "しんかんせんがはやい")
        mock_exit.assert_called_once_with(0)

    @patch("sys.exit")
    @patch("sys.stderr", new_callable=io.StringIO)
    def test_main_invalid_shift(self, mock_stderr, mock_exit):
        """
        負のシフト量が指定された場合にエラー終了することを検証します。
        """
        mock_exit.side_effect = SystemExit(1)
        test_args = ["japanesformer", "テスト", "-s", "-1"]
        with patch.object(sys, "argv", test_args):
            with self.assertRaises(SystemExit):
                main()
            
        self.assertIn("エラー: シフト量", mock_stderr.getvalue())
        mock_exit.assert_called_once_with(1)

if __name__ == "__main__":
    unittest.main()
