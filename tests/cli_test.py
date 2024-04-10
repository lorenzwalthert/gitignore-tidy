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
