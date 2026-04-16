import os
import shlex
import subprocess

SMK_CMD = "python -m snakemk_util.main --snakefile tests/data/test_rule_args/Snakefile"


def test_main():
    assert os.system(f'{SMK_CMD} --rule "all"') == 0
    assert os.system(f'{SMK_CMD} --rule "all" --gen-preamble "BashScript"') == 0
    assert os.system(f'{SMK_CMD} --rule "all" --gen-preamble "PythonScript"') == 0
    assert os.system(f'{SMK_CMD} --rule "all" --gen-preamble "PythonJupyterNotebook"') == 0

    # try executing the preamble
    exec(
        subprocess.run(
            shlex.split(f'{SMK_CMD} --rule "all" --gen-preamble "PythonScript"'),
            stdout=subprocess.PIPE,
        ).stdout
    )
