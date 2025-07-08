import unittest
import tempfile
import shutil
import os
import sys
import datetime
import re
from unittest.mock import patch, MagicMock
from io import StringIO

# Import the modules to test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zettelkasten_normalizer import utils, file_operations, yfm_processor, link_processor, config, frontmatter_parser


class TestUtilityFunctions(unittest.TestCase):
    """ユーティリティ関数のテスト"""

    def test_get_file_name(self):
        """ファイル名解析のテスト"""
        # 通常のファイル
        result = utils.get_file_name("/path/to/test.md")
        self.assertEqual(result, ("test.md", "test", ".md"))
        
        # 拡張子なし
        result = utils.get_file_name("/path/to/test")
        self.assertEqual(result, ("test", "test", ""))
        
        # 日本語ファイル名
        result = utils.get_file_name("/path/to/テスト.md")
        self.assertEqual(result, ("テスト.md", "テスト", ".md"))

    def test_get_dir_name(self):
        """ディレクトリ名解析のテスト"""
        result = utils.get_dir_name("/path/to/test.md")
        self.assertEqual(result, ("/path/to", "to"))
        
        result = utils.get_dir_name("/home/user/documents/file.txt")
        self.assertEqual(result, ("/home/user/documents", "documents"))

    def test_format_date(self):
        """日付フォーマットのテスト"""
        # 固定のタイムスタンプをテスト
        timestamp = 1609459200  # 2021-01-01 00:00:00 UTC
        result = utils.format_date(timestamp)
        # タイムゾーンによる差異を考慮し、年月日のみチェック
        self.assertTrue(result.startswith("2021-01-01") or result.startswith("2020-12-31"))

    def test_format_uid_from_date(self):
        """UID形式の日付フォーマットのテスト"""
        timestamp = 1609459200  # 2021-01-01 00:00:00 UTC
        result = utils.format_uid_from_date(timestamp)
        # タイムゾーンによる差異を考慮
        self.assertTrue(result.startswith("20210101") or result.startswith("20201231"))

    def test_check_note_type(self):
        """ファイルタイプチェックのテスト"""
        # ノートファイル
        self.assertTrue(file_operations.check_note_type("/path/test.md", "note"))
        self.assertTrue(file_operations.check_note_type("/path/test.txt", "note"))
        self.assertFalse(file_operations.check_note_type("/path/test.pdf", "note"))
        
        # 画像ファイル
        self.assertTrue(file_operations.check_note_type("/path/test.png", "image"))
        self.assertTrue(file_operations.check_note_type("/path/test.jpg", "image"))
        self.assertFalse(file_operations.check_note_type("/path/test.md", "image"))

    def test_check_note_has_uid(self):
        """UIDチェックのテスト"""
        # 有効なUID（32文字の16進数）
        self.assertTrue(file_operations.check_note_has_uid("/path/abcdef0123456789abcdef0123456789.md"))
        
        # 無効なUID
        self.assertFalse(file_operations.check_note_has_uid("/path/test.md"))
        self.assertFalse(file_operations.check_note_has_uid("/path/short123.md"))
        self.assertFalse(file_operations.check_note_has_uid("/path/abcdef0123456789ABCDEF0123456789.md"))  # 大文字

    def test_build_filepath_by_uid(self):
        """UIDによるファイルパス構築のテスト"""
        uid = "abcdef0123456789abcdef0123456789"
        path = "/test/path"
        
        result = file_operations.build_filepath_by_uid(uid, path, ".md")
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
        
        # logger をモック
        mock_logger = MagicMock()
        yfm_processor.logger = mock_logger
        
        try:
            result = yfm_processor.create_tag_line_from_lines(lines)
        finally:
            if hasattr(yfm_processor, 'logger'):
                delattr(yfm_processor, 'logger')
        
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
        
        result = file_operations.get_files(test_file, "note")
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
        note_files = file_operations.get_files(self.test_dir, "note")
        self.assertEqual(len(note_files), 2)
        self.assertTrue(any("test1.md" in f for f in note_files))
        self.assertTrue(any("test2.txt" in f for f in note_files))
        
        # 画像ファイルのみ取得
        image_files = file_operations.get_files(self.test_dir, "image")
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
        
        result = file_operations.get_files(self.test_dir, "note")
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
        
        result = file_operations.get_files(self.test_dir, "note")
        self.assertEqual(len(result), 1)
        self.assertTrue(any("normal.md" in f for f in result))

    def test_get_new_filepath_with_uid(self):
        """UID付きファイルパス生成のテスト"""
        test_file = os.path.join(self.test_dir, "test.md")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        result = file_operations.get_new_filepath_with_uid(test_file, self.test_dir)
        
        # 結果がUUID形式であることを確認
        filename = os.path.basename(result)
        name, ext = os.path.splitext(filename)
        self.assertEqual(ext, ".md")
        self.assertEqual(len(name), 32)
        self.assertTrue(all(c in "0123456789abcdef" for c in name))


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
        yfm_processor.logger = mock_logger
        
        try:
            # 関数を実行
            yfm_processor.check_and_create_yfm([test_file])
            
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
            if hasattr(yfm_processor, 'logger'):
                delattr(yfm_processor, 'logger')

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
        yfm_processor.logger = mock_logger
        
        try:
            # 関数を実行
            yfm_processor.check_and_create_yfm([test_file])
        finally:
            if hasattr(yfm_processor, 'logger'):
                delattr(yfm_processor, 'logger')
        
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
        yfm_processor.logger = mock_logger
        
        try:
            yfm_processor.writing_lines_without_hashtags(test_file, lines)
        finally:
            if hasattr(yfm_processor, 'logger'):
                delattr(yfm_processor, 'logger')
        
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
        
        # loggerをモック
        mock_logger = MagicMock()
        link_processor.logger = mock_logger
        
        try:
            # リンク置換を実行
            with patch('zettelkasten_normalizer.file_operations.get_files') as mock_get_files:
                mock_get_files.return_value = [link_file]
                result = link_processor.substitute_wikilinks_to_markdown_links(
                    source_file, target_file, self.test_dir
                )
        finally:
            if hasattr(link_processor, 'logger'):
                delattr(link_processor, 'logger')
        
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
        # テストファイルを作成
        test_file = os.path.join(self.test_dir, "test_note.md")
        with open(test_file, 'w') as f:
            f.write("""---
title: Test Note
---

# Test Note

This is a test note.""")
        
        # loggerをモック
        mock_logger = MagicMock()
        link_processor.logger = mock_logger
        
        try:
            # rename_notes_with_links を実行
            with patch('zettelkasten_normalizer.link_processor.substitute_wikilinks_to_markdown_links') as mock_substitute:
                mock_substitute.return_value = False
                link_processor.rename_notes_with_links([test_file], self.test_dir)
        finally:
            if hasattr(link_processor, 'logger'):
                delattr(link_processor, 'logger')
        
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
            result = utils.query_yes_no("Test question?")
            self.assertTrue(result)
        
        # "no"の場合
        with patch('builtins.input', return_value='no'):
            result = utils.query_yes_no("Test question?")
            self.assertFalse(result)
        
        # デフォルト値（空入力）の場合
        with patch('builtins.input', return_value=''):
            result = utils.query_yes_no("Test question?", default="yes")
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
            from zettelkasten_normalizer import normalization_zettel
            args = normalization_zettel.parse_arguments()
            
            # 引数が正しく解析されることを確認
            self.assertEqual(args.root, '/test/path')
            self.assertEqual(args.target, '/test/target')
            self.assertTrue(args.yes)
            
        finally:
            sys.argv = original_argv


class TestFrontMatterParser(unittest.TestCase):
    """フロントマターパーサーのテスト"""

    def test_yaml_parser(self):
        """YAMLパーサーのテスト"""
        parser = frontmatter_parser.FrontMatterParser("yaml")
        
        # YAML形式のコンテンツ
        content = """---
title: Test Note
tags: [test, example]
draft: false
---

# Test Content

This is a test note."""
        
        metadata, body = parser.parse_frontmatter(content)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["title"], "Test Note")
        self.assertEqual(metadata["tags"], "[test, example]")
        self.assertEqual(metadata["draft"], "false")
        self.assertIn("# Test Content", body)

    def test_toml_parser(self):
        """TOMLパーサーのテスト（利用可能な場合）"""
        try:
            parser = frontmatter_parser.FrontMatterParser("toml")
        except ImportError:
            self.skipTest("TOML parser not available")
        
        # TOML形式のコンテンツ
        content = """+++
title = "Test Note"
tags = ["test", "example"]
draft = false
+++

# Test Content

This is a test note."""
        
        metadata, body = parser.parse_frontmatter(content)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["title"], "Test Note")
        self.assertEqual(metadata["tags"], ["test", "example"])
        self.assertEqual(metadata["draft"], False)
        self.assertIn("# Test Content", body)

    def test_json_parser(self):
        """JSONパーサーのテスト"""
        parser = frontmatter_parser.FrontMatterParser("json")
        
        # JSON形式のコンテンツ
        content = """{
  "title": "Test Note",
  "tags": ["test", "example"],
  "draft": false
}

# Test Content

This is a test note."""
        
        metadata, body = parser.parse_frontmatter(content)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["title"], "Test Note")
        self.assertEqual(metadata["tags"], ["test", "example"])
        self.assertEqual(metadata["draft"], False)
        self.assertIn("# Test Content", body)

    def test_format_detection(self):
        """フォーマット検出のテスト"""
        parser = frontmatter_parser.FrontMatterParser("yaml")
        
        # YAML
        yaml_content = "---\ntitle: test\n---\ncontent"
        self.assertEqual(parser.detect_format(yaml_content), "yaml")
        
        # TOML
        toml_content = "+++\ntitle = \"test\"\n+++\ncontent"
        self.assertEqual(parser.detect_format(toml_content), "toml")
        
        # JSON
        json_content = '{\n  "title": "test"\n}\ncontent'
        self.assertEqual(parser.detect_format(json_content), "json")
        
        # No front matter
        plain_content = "# Title\nRegular content"
        self.assertIsNone(parser.detect_format(plain_content))

    def test_yaml_serialization(self):
        """YAMLシリアライゼーションのテスト"""
        parser = frontmatter_parser.FrontMatterParser("yaml")
        
        metadata = {
            "title": "Test Note",
            "tags": "[test, example]",
            "draft": "false"
        }
        content = "# Test Content\n\nThis is a test note."
        
        result = parser.serialize_frontmatter(metadata, content)
        
        self.assertIn("---", result)
        self.assertIn("title: Test Note", result)
        self.assertIn("tags: [test, example]", result)
        self.assertIn("draft: false", result)
        self.assertIn("# Test Content", result)

    def test_toml_serialization(self):
        """TOMLシリアライゼーションのテスト（利用可能な場合）"""
        try:
            parser = frontmatter_parser.FrontMatterParser("toml")
        except ImportError:
            self.skipTest("TOML parser not available")
        
        metadata = {
            "title": "Test Note",
            "tags": "[test, example]",
            "draft": "false"
        }
        content = "# Test Content\n\nThis is a test note."
        
        result = parser.serialize_frontmatter(metadata, content)
        
        self.assertIn("+++", result)
        self.assertIn('title = "Test Note"', result)
        self.assertIn('tags = [test, example]', result)
        self.assertIn('draft = false', result)
        self.assertIn("# Test Content", result)

    def test_json_serialization(self):
        """JSONシリアライゼーションのテスト"""
        parser = frontmatter_parser.FrontMatterParser("json")
        
        metadata = {
            "title": "Test Note",
            "tags": "[\"test\", \"example\"]",
            "draft": "false"
        }
        content = "# Test Content\n\nThis is a test note."
        
        result = parser.serialize_frontmatter(metadata, content)
        
        self.assertIn('"title": "Test Note"', result)
        # JSONの配列は複数行で表示される可能性があるため、柔軟にチェック
        self.assertIn('"tags":', result)
        self.assertIn('"test"', result)
        self.assertIn('"example"', result)
        self.assertIn('"draft": false', result)
        self.assertIn("# Test Content", result)


class TestFrontMatterIntegration(unittest.TestCase):
    """フロントマター統合テスト"""

    def setUp(self):
        """テスト用の一時ディレクトリを作成"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def test_toml_frontmatter_creation(self):
        """TOMLフロントマター作成のテスト（利用可能な場合）"""
        try:
            frontmatter_parser.FrontMatterParser("toml")
        except ImportError:
            self.skipTest("TOML parser not available")
        
        # TOMLフロントマターなしのファイルを作成
        test_file = os.path.join(self.test_dir, "test.md")
        with open(test_file, 'w') as f:
            f.write("# Test Note\n\nThis is a test note with #tag1.")
        
        # loggerをモック
        mock_logger = MagicMock()
        yfm_processor.logger = mock_logger
        
        try:
            # TOMLフロントマターでフロントマター作成を実行
            yfm_processor.check_and_create_yfm([test_file], "toml")
            
            # ファイルを読み込んで確認
            with open(test_file, 'r') as f:
                content = f.read()
            
            # TOMLフロントマターが追加されていることを確認
            self.assertTrue(content.startswith("+++\n"))
            self.assertIn('title = "test"', content)
            self.assertIn('aliases = []', content)
            self.assertIn('draft = false', content)
            
        finally:
            if hasattr(yfm_processor, 'logger'):
                delattr(yfm_processor, 'logger')

    def test_json_frontmatter_creation(self):
        """JSONフロントマター作成のテスト"""
        # JSONフロントマターなしのファイルを作成
        test_file = os.path.join(self.test_dir, "test.md")
        with open(test_file, 'w') as f:
            f.write("# Test Note\n\nThis is a test note with #tag1.")
        
        # loggerをモック
        mock_logger = MagicMock()
        yfm_processor.logger = mock_logger
        
        try:
            # JSONフロントマターでフロントマター作成を実行
            yfm_processor.check_and_create_yfm([test_file], "json")
            
            # ファイルを読み込んで確認
            with open(test_file, 'r') as f:
                content = f.read()
            
            # JSONフロントマターが追加されていることを確認
            self.assertTrue(content.startswith("{\n"))
            self.assertIn('"title": "test"', content)
            self.assertIn('"aliases": []', content)
            self.assertIn('"draft": false', content)
            
        finally:
            if hasattr(yfm_processor, 'logger'):
                delattr(yfm_processor, 'logger')


class TestCrossPlatformSupport(unittest.TestCase):
    """クロスプラットフォーム対応のテスト"""

    def setUp(self):
        """テスト用の一時ディレクトリを作成"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def test_normalize_line_endings(self):
        """改行コード正規化のテスト"""
        # Windows CRLF
        windows_content = "line1\r\nline2\r\nline3\r\n"
        normalized = utils.normalize_line_endings(windows_content)
        self.assertEqual(normalized, "line1\nline2\nline3\n")
        
        # Old Mac CR
        mac_content = "line1\rline2\rline3\r"
        normalized = utils.normalize_line_endings(mac_content)
        self.assertEqual(normalized, "line1\nline2\nline3\n")
        
        # Unix LF (should remain unchanged)
        unix_content = "line1\nline2\nline3\n"
        normalized = utils.normalize_line_endings(unix_content)
        self.assertEqual(normalized, "line1\nline2\nline3\n")
        
        # Mixed line endings
        mixed_content = "line1\r\nline2\nline3\r"
        normalized = utils.normalize_line_endings(mixed_content)
        self.assertEqual(normalized, "line1\nline2\nline3\n")

    def test_cross_platform_file_operations(self):
        """クロスプラットフォームファイル操作のテスト"""
        test_file = os.path.join(self.test_dir, "test.md")
        
        # Windows style content with CRLF
        original_content = "# Test\r\n\r\nThis is a test with CRLF line endings.\r\n"
        
        # Write and read back
        utils.write_file_cross_platform(test_file, original_content)
        read_content = utils.read_file_cross_platform(test_file)
        
        # Content should be normalized to LF
        expected_content = "# Test\n\nThis is a test with CRLF line endings.\n"
        self.assertEqual(read_content, expected_content)

    def test_path_normalization(self):
        """パス正規化のテスト"""
        # Test various path separators
        if os.name == 'nt':  # Windows
            # Forward slashes should be converted to backslashes on Windows
            path = "path/to/file.md"
            normalized = utils.normalize_path(path)
            self.assertEqual(normalized, "path\\to\\file.md")
        else:  # Unix-like systems
            # Backslashes should be preserved but path should be normalized
            path = "path/to/../to/file.md"
            normalized = utils.normalize_path(path)
            self.assertEqual(normalized, "path/to/file.md")
        
        # Test with double separators
        path_with_double = "path//to//file.md"
        normalized = utils.normalize_path(path_with_double)
        expected_sep = utils.get_platform_path_separator()
        expected = f"path{expected_sep}to{expected_sep}file.md"
        self.assertEqual(normalized, expected)

    def test_frontmatter_with_different_line_endings(self):
        """異なる改行コードでのフロントマター処理テスト"""
        test_file = os.path.join(self.test_dir, "test.md")
        
        # Create content with Windows line endings
        content_crlf = "# Test Note\r\n\r\nThis is a test note with #tag1.\r\n"
        
        # Write file with Windows line endings
        with open(test_file, 'w', newline='\r\n') as f:
            f.write(content_crlf)
        
        # loggerをモック
        mock_logger = MagicMock()
        yfm_processor.logger = mock_logger
        
        try:
            # フロントマター作成を実行
            yfm_processor.check_and_create_yfm([test_file], "yaml")
            
            # ファイルを読み込んで確認
            result_content = utils.read_file_cross_platform(test_file)
            
            # YAMLフロントマターが追加されていることを確認
            self.assertTrue(result_content.startswith("---\n"))
            self.assertIn("title: test", result_content)
            self.assertIn("tag1", result_content)
            
        finally:
            if hasattr(yfm_processor, 'logger'):
                delattr(yfm_processor, 'logger')

    def test_unicode_file_handling(self):
        """Unicode文字を含むファイルの処理テスト"""
        test_file = os.path.join(self.test_dir, "日本語ファイル.md")
        
        # Unicode content with Japanese characters
        unicode_content = "# テストノート\n\n日本語のコンテンツです。\n"
        
        # Write and read back
        utils.write_file_cross_platform(test_file, unicode_content)
        read_content = utils.read_file_cross_platform(test_file)
        
        self.assertEqual(read_content, unicode_content)


if __name__ == '__main__':
    # テストの実行
    unittest.main(verbosity=2)