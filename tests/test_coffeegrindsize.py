from click.testing import CliRunner
from coffeegrindsize.scripts.coffeegrindsize import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
