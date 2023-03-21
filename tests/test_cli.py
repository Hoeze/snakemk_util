import os

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