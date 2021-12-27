import os
import tempfile

from typer.testing import CliRunner

from gitignore_tidy.core import app
runner = CliRunner()


def test_cli():

    contents = """\
    # secion1
    a
    b
    !a/b

    # section 55
    x
    *.pdf
    """

    with tempfile.TemporaryDirectory() as temp_dir:
        g1 = os.path.join(temp_dir, '.gitignore')
        with open(g1, 'w') as file:
            file.write(contents)

        dir2 = os.path.join(temp_dir, 'docs')
        os.mkdir(dir2)
        g2 = os.path.join(dir2, '.gitignore')
        with open(g2, 'w') as file:
            file.write(contents)

        result = runner.invoke(app, [g1, g2])
        assert result.exit_code == 0
        assert 'Successfully written' in result.stdout
        result = runner.invoke(app, [g1])
        assert result.exit_code == 0
        assert 'already' in result.stdout
