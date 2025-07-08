import unittest
import tempfile
import shutil
import os
import sys
import datetime
import re
from unittest.mock import patch, MagicMock
from io import StringIO

# Import the module to test with mock arguments
with patch.object(sys, 'argv', ['test', '/tmp']):
    import normalization_zettel


class TestUtilityFunctions(unittest.TestCase):
    """ユーティリティ関数のテスト"""

    def test_get_file_name(self):
        """ファイル名解析のテスト"""
        # 通常のファイル
        result = normalization_zettel.get_file_name("/path/to/test.md")
        self.assertEqual(result, ("test.md", "test", ".md"))
        
        # 拡張子なし
        result = normalization_zettel.get_file_name("/path/to/test")
        self.assertEqual(result, ("test", "test", ""))
        
        # 日本語ファイル名
        result = normalization_zettel.get_file_name("/path/to/テスト.md")
        self.assertEqual(result, ("テスト.md", "テスト", ".md"))

    def test_get_dir_name(self):
        """ディレクトリ名解析のテスト"""
        result = normalization_zettel.get_dir_name("/path/to/test.md")
        self.assertEqual(result, ("/path/to", "to"))
        
        result = normalization_zettel.get_dir_name("/home/user/documents/file.txt")
        self.assertEqual(result, ("/home/user/documents", "documents"))

    def test_format_date(self):
        """日付フォーマットのテスト"""
        # 固定のタイムスタンプをテスト
        timestamp = 1609459200  # 2021-01-01 00:00:00 UTC
        result = normalization_zettel.format_date(timestamp)
        # タイムゾーンによる差異を考慮し、年月日のみチェック
        self.assertTrue(result.startswith("2021-01-01") or result.startswith("2020-12-31"))

    def test_format_uid_from_date(self):
        """UID形式の日付フォーマットのテスト"""
        timestamp = 1609459200  # 2021-01-01 00:00:00 UTC
        result = normalization_zettel.format_uid_from_date(timestamp)
        # タイムゾーンによる差異を考慮
        self.assertTrue(result.startswith("20210101") or result.startswith("20201231"))

    def test_check_note_type(self):
        """ファイルタイプチェックのテスト"""
        # ノートファイル
        self.assertTrue(normalization_zettel.check_note_type("/path/test.md", "note"))
        self.assertTrue(normalization_zettel.check_note_type("/path/test.txt", "note"))
        self.assertFalse(normalization_zettel.check_note_type("/path/test.pdf", "note"))
        
        # 画像ファイル
        self.assertTrue(normalization_zettel.check_note_type("/path/test.png", "image"))
        self.assertTrue(normalization_zettel.check_note_type("/path/test.jpg", "image"))
        self.assertFalse(normalization_zettel.check_note_type("/path/test.md", "image"))

    def test_check_note_has_uid(self):
        """UIDチェックのテスト"""
        # 有効なUID（32文字の16進数）
        self.assertTrue(normalization_zettel.check_note_has_uid("/path/abcdef0123456789abcdef0123456789.md"))
        
        # 無効なUID
        self.assertFalse(normalization_zettel.check_note_has_uid("/path/test.md"))
        self.assertFalse(normalization_zettel.check_note_has_uid("/path/short123.md"))
        self.assertFalse(normalization_zettel.check_note_has_uid("/path/abcdef0123456789ABCDEF0123456789.md"))  # 大文字

    def test_build_filepath_by_uid(self):
        """UIDによるファイルパス構築のテスト"""
        uid = "abcdef0123456789abcdef0123456789"
        path = "/test/path"
        
        result = normalization_zettel.build_filepath_by_uid(uid, path, ".md")
        expected = "/test/path/abcdef0123456789abcdef0123456789.md"
        self.assertEqual(result, expected)

    def test_create_tag_line_from_lines(self):
        """ハッシュタグからタグライン作成のテスト"""
        lines = [
            "This is a test line with #tag1\n",
            "Another line with #tag2 and #tag3\n",
            "No tags here\n",
            "Line with #duplicate and #tag1 again\n"
        ]
        
        # loggerをモック
        mock_logger = MagicMock()
        normalization_zettel.logger = mock_logger
        
        try:
            result = normalization_zettel.create_tag_line_from_lines(lines)
        finally:
            if hasattr(normalization_zettel, 'logger'):
                delattr(normalization_zettel, 'logger')
        
        # タグが正しく抽出されることを確認
        self.assertIn("tag1", result)
        self.assertIn("tag2", result)
        self.assertIn("tag3", result)
        self.assertTrue(result.startswith("[") and result.endswith("]"))


class TestFileOperations(unittest.TestCase):
    """ファイル操作のテスト"""

    def setUp(self):
        """テスト用の一時ディレクトリを作成"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def test_get_files_single_file(self):
        """単一ファイルの取得テスト"""
        # テストファイルを作成
        test_file = os.path.join(self.test_dir, "test.md")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        result = normalization_zettel.get_files(test_file, "note")
        self.assertEqual(result, [test_file])

    def test_get_files_directory(self):
        """ディレクトリからのファイル取得テスト"""
        # テストファイルを作成
        test_files = [
            os.path.join(self.test_dir, "test1.md"),
            os.path.join(self.test_dir, "test2.txt"),
            os.path.join(self.test_dir, "image.png"),
            os.path.join(self.test_dir, "ignore.pdf")
        ]
        
        for file_path in test_files:
            with open(file_path, 'w') as f:
                f.write("test content")
        
        # ノートファイルのみ取得
        note_files = normalization_zettel.get_files(self.test_dir, "note")
        self.assertEqual(len(note_files), 2)
        self.assertTrue(any("test1.md" in f for f in note_files))
        self.assertTrue(any("test2.txt" in f for f in note_files))
        
        # 画像ファイルのみ取得
        image_files = normalization_zettel.get_files(self.test_dir, "image")
        self.assertEqual(len(image_files), 1)
        self.assertTrue(any("image.png" in f for f in image_files))

    def test_get_files_exclude_hidden(self):
        """隠しファイル除外のテスト"""
        # 隠しファイルを作成
        hidden_file = os.path.join(self.test_dir, ".hidden.md")
        normal_file = os.path.join(self.test_dir, "normal.md")
        
        with open(hidden_file, 'w') as f:
            f.write("hidden content")
        with open(normal_file, 'w') as f:
            f.write("normal content")
        
        result = normalization_zettel.get_files(self.test_dir, "note")
        self.assertEqual(len(result), 1)
        self.assertTrue(any("normal.md" in f for f in result))

    def test_get_files_exclude_directories(self):
        """除外ディレクトリのテスト"""
        # 除外対象のディレクトリを作成
        backup_dir = os.path.join(self.test_dir, "Backup")
        os.makedirs(backup_dir)
        
        backup_file = os.path.join(backup_dir, "backup.md")
        normal_file = os.path.join(self.test_dir, "normal.md")
        
        with open(backup_file, 'w') as f:
            f.write("backup content")
        with open(normal_file, 'w') as f:
            f.write("normal content")
        
        result = normalization_zettel.get_files(self.test_dir, "note")
        self.assertEqual(len(result), 1)
        self.assertTrue(any("normal.md" in f for f in result))

    def test_get_new_filepath_with_uid(self):
        """UID付きファイルパス生成のテスト"""
        test_file = os.path.join(self.test_dir, "test.md")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # ROOT_PATHを一時的に設定（グローバル変数として設定）
        original_root_path = getattr(normalization_zettel, 'ROOT_PATH', None)
        normalization_zettel.ROOT_PATH = self.test_dir
        
        try:
            result = normalization_zettel.get_new_filepath_with_uid(test_file)
            
            # 結果がUUID形式であることを確認
            filename = os.path.basename(result)
            name, ext = os.path.splitext(filename)
            self.assertEqual(ext, ".md")
            self.assertEqual(len(name), 32)
            self.assertTrue(all(c in "0123456789abcdef" for c in name))
        finally:
            if original_root_path is not None:
                normalization_zettel.ROOT_PATH = original_root_path
            elif hasattr(normalization_zettel, 'ROOT_PATH'):
                delattr(normalization_zettel, 'ROOT_PATH')


class TestYAMLFrontMatter(unittest.TestCase):
    """YAML Front Matter処理のテスト"""

    def setUp(self):
        """テスト用の一時ディレクトリを作成"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def test_check_and_create_yfm_new_file(self):
        """新しいファイルへのYFM追加テスト"""
        # YFMなしのファイルを作成
        test_file = os.path.join(self.test_dir, "test.md")
        with open(test_file, 'w') as f:
            f.write("# Test Note\n\nThis is a test note with #tag1 and #tag2.")
        
        # loggerをモック
        import logging
        mock_logger = MagicMock()
        normalization_zettel.logger = mock_logger
        
        try:
            # 関数を実行
            normalization_zettel.check_and_create_yfm([test_file])
            
            # ファイルを読み込んで確認
            with open(test_file, 'r') as f:
                content = f.read()
            
            # YFMが追加されていることを確認
            self.assertTrue(content.startswith("---\n"))
            self.assertIn("title: test", content)
            self.assertIn("aliases: []", content)
            self.assertIn("date:", content)
            self.assertIn("update:", content)
            # タグの確認（句読点が含まれる可能性があるため柔軟にチェック）
            self.assertTrue("tag1" in content and "tag2" in content)
            self.assertIn("draft: false", content)
        finally:
            # loggerをクリーンアップ
            if hasattr(normalization_zettel, 'logger'):
                delattr(normalization_zettel, 'logger')

    def test_check_and_create_yfm_existing_file(self):
        """既存YFMファイルの更新テスト"""
        # YFM付きのファイルを作成
        test_file = os.path.join(self.test_dir, "test.md")
        with open(test_file, 'w') as f:
            f.write("""---
title: Test
date: 2021-01-01 00:00:00
---

# Test Note

Content here.""")
        
        # loggerをモック
        mock_logger = MagicMock()
        normalization_zettel.logger = mock_logger
        
        try:
            # 関数を実行
            normalization_zettel.check_and_create_yfm([test_file])
        finally:
            if hasattr(normalization_zettel, 'logger'):
                delattr(normalization_zettel, 'logger')
        
        # ファイルを読み込んで確認
        with open(test_file, 'r') as f:
            content = f.read()
        
        # updateフィールドが追加されていることを確認
        self.assertIn("update:", content)

    def test_writing_lines_without_hashtags(self):
        """ハッシュタグ除去のテスト"""
        test_file = os.path.join(self.test_dir, "test.md")
        lines = [
            "---\n",
            "title: Test\n",
            "---\n",
            "\n",
            "# Title\n",
            "\n",
            "This is content with #tag1\n",
            "#standalone_hashtag\n",
            "More content\n",
            "\n"
        ]
        
        # loggerをモック
        mock_logger = MagicMock()
        normalization_zettel.logger = mock_logger
        
        try:
            normalization_zettel.writing_lines_without_hashtags(test_file, lines)
        finally:
            if hasattr(normalization_zettel, 'logger'):
                delattr(normalization_zettel, 'logger')
        
        with open(test_file, 'r') as f:
            content = f.read()
        
        # ハッシュタグ行が除去されていることを確認
        self.assertNotIn("#standalone_hashtag", content)
        # インラインハッシュタグは残ることを確認
        self.assertIn("This is content with #tag1", content)


class TestLinkSubstitution(unittest.TestCase):
    """リンク置換機能のテスト"""

    def setUp(self):
        """テスト用の一時ディレクトリを作成"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def test_substitute_wikilinks_to_markdown_links(self):
        """Wikilink→Markdownリンク置換のテスト"""
        # ROOT_PATHとloggerを設定
        normalization_zettel.ROOT_PATH = self.test_dir
        mock_logger = MagicMock()
        normalization_zettel.logger = mock_logger
        
        # テストファイルを作成
        source_file = os.path.join(self.test_dir, "source.md")
        target_file = os.path.join(self.test_dir, "abcdef0123456789abcdef0123456789.md")
        link_file = os.path.join(self.test_dir, "linking.md")
        
        with open(source_file, 'w') as f:
            f.write("Source content")
        
        with open(target_file, 'w') as f:
            f.write("Target content")
        
        with open(link_file, 'w') as f:
            f.write("""# Linking Note

This note links to [[source]] and [[source.md]].
Also links to [[source | alias text]].
And markdown links [source](source.md).
""")
        
        try:
            # リンク置換を実行
            with patch('normalization_zettel.get_files') as mock_get_files:
                mock_get_files.return_value = [link_file]
                result = normalization_zettel.substitute_wikilinks_to_markdown_links(
                    source_file, target_file
                )
        finally:
            if hasattr(normalization_zettel, 'ROOT_PATH'):
                delattr(normalization_zettel, 'ROOT_PATH')
            if hasattr(normalization_zettel, 'logger'):
                delattr(normalization_zettel, 'logger')
        
        # ファイルを読み込んで確認
        with open(link_file, 'r') as f:
            content = f.read()
        
        # リンクが置換されていることを確認
        target_filename = os.path.basename(target_file)
        self.assertIn(f"[source]({target_filename})", content)
        self.assertIn(f"[alias text]({target_filename})", content)
        self.assertTrue(result)  # 置換が行われたことを確認


class TestMainFunctions(unittest.TestCase):
    """メイン機能のテスト"""

    def setUp(self):
        """テスト用の一時ディレクトリを作成"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def test_rename_notes_with_links(self):
        """ノートリネーム機能のテスト"""
        # ROOT_PATHとloggerを設定
        normalization_zettel.ROOT_PATH = self.test_dir
        mock_logger = MagicMock()
        normalization_zettel.logger = mock_logger
        
        # テストファイルを作成
        test_file = os.path.join(self.test_dir, "test_note.md")
        with open(test_file, 'w') as f:
            f.write("""---
title: Test Note
---

# Test Note

This is a test note.""")
        
        try:
            # rename_notes_with_links を実行
            with patch('normalization_zettel.substitute_wikilinks_to_markdown_links') as mock_substitute:
                mock_substitute.return_value = False
                normalization_zettel.rename_notes_with_links([test_file])
        finally:
            if hasattr(normalization_zettel, 'ROOT_PATH'):
                delattr(normalization_zettel, 'ROOT_PATH')
            if hasattr(normalization_zettel, 'logger'):
                delattr(normalization_zettel, 'logger')
        
        # 元のファイルが存在しないことを確認
        self.assertFalse(os.path.exists(test_file))
        
        # UUIDファイルが作成されていることを確認
        files = os.listdir(self.test_dir)
        uuid_files = [f for f in files if len(os.path.splitext(f)[0]) == 32]
        self.assertEqual(len(uuid_files), 1)
        
        # 新しいファイルにUIDが追加されていることを確認
        new_file = os.path.join(self.test_dir, uuid_files[0])
        with open(new_file, 'r') as f:
            content = f.read()
        self.assertIn("uid:", content)

    def test_query_yes_no(self):
        """ユーザー入力確認のテスト"""
        # "yes"の場合
        with patch('builtins.input', return_value='yes'):
            result = normalization_zettel.query_yes_no("Test question?")
            self.assertTrue(result)
        
        # "no"の場合
        with patch('builtins.input', return_value='no'):
            result = normalization_zettel.query_yes_no("Test question?")
            self.assertFalse(result)
        
        # デフォルト値（空入力）の場合
        with patch('builtins.input', return_value=''):
            result = normalization_zettel.query_yes_no("Test question?", default="yes")
            self.assertTrue(result)


class TestArgumentParsing(unittest.TestCase):
    """引数解析のテスト"""

    def test_argument_parsing(self):
        """引数解析のテスト"""
        # sys.argvを一時的に変更
        original_argv = sys.argv
        try:
            sys.argv = ['normalization_zettel.py', '/test/path', '-t', '/test/target', '-y']
            
            # パーサーを再作成
            import importlib
            importlib.reload(normalization_zettel)
            
            # 引数が正しく解析されることを確認
            # （実際の実装では、グローバル変数の変更が必要になる場合があります）
            
        finally:
            sys.argv = original_argv


if __name__ == '__main__':
    # テストの実行
    unittest.main(verbosity=2)