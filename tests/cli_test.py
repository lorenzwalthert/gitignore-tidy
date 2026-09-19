from typer.testing import CliRunner

from gitignore_tidy.cli import app
from tests.core_test import TestTidyFile

runner = CliRunner()


class TestCLI(TestTidyFile):

    def test_unclean_multiple(self, temp_dir, untidy_contents):

        path_first = self.write(temp_dir, contents=untidy_contents)

        path_second = self.write(temp_dir / "docs", contents=untidy_contents)

        result = runner.invoke(app, [str(path_first), str(path_second)])
        assert result.exit_code == 0

    def test_default_keeps_negation_order(self, temp_dir):
        path = self.write(temp_dir, contents="*csv\n!*aut.csv\n")
        result = runner.invoke(app, [str(path)])
        assert result.exit_code == 0
        assert path.read_text() == "*csv\n!*aut.csv\n"

    def test_negations_last_group(self, temp_dir):
        path = self.write(temp_dir, contents="y\n!y/keep\nx\n")
        result = runner.invoke(app, [str(path), "--negations-last=group"])
        assert result.exit_code == 0
        assert path.read_text() == "x\ny\n!y/keep\n"

    def test_negations_last_eof(self, temp_dir):
        path = self.write(temp_dir, contents="# a\n*.log\n!keep.log\n# b\nbuild/\n")
        result = runner.invoke(app, [str(path), "--negations-last=eof"])
        assert result.exit_code == 0
        assert path.read_text() == "# a\n*.log\n# b\nbuild/\n\n!keep.log\n"

    def test_negations_last_rejects_unknown_value(self, temp_dir):
        path = self.write(temp_dir, contents="a\n")
        result = runner.invoke(app, [str(path), "--negations-last=nope"])
        assert result.exit_code != 0
