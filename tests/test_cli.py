import os
import subprocess
import shlex


def test_main():
    assert os.system(
        """python -m snakemk_util.main --snakefile tests/data/test_rule_args/Snakefile --rule "all" """
    ) == 0
    assert os.system(
        """python -m snakemk_util.main --snakefile tests/data/test_rule_args/Snakefile --rule "all" --gen-preamble "BashScript" """
    ) == 0
    assert os.system(
        """python -m snakemk_util.main --snakefile tests/data/test_rule_args/Snakefile --rule "all" --gen-preamble "PythonScript" """
    ) == 0
    assert os.system(
        """python -m snakemk_util.main --snakefile tests/data/test_rule_args/Snakefile --rule "all" --gen-preamble "PythonJupyterNotebook" """
    ) == 0

    # try executing the preamble
    exec(subprocess.run(
        shlex.split(
            """python -m snakemk_util.main --snakefile tests/data/test_rule_args/Snakefile --rule "all" --gen-preamble "PythonScript" """),
        stdout=subprocess.PIPE
    ).stdout)
