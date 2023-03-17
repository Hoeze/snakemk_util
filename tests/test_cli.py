import os

def test_main():
    assert os.system(
        """python -m snakemk_util.main --snakefile tests/data/test_rule_args/Snakefile --rule "all" --script_flavor "BashScript" """
    ) == 0
    assert os.system(
        """python -m snakemk_util.main --snakefile tests/data/test_rule_args/Snakefile --rule "all" --script_flavor "PythonScript" """
    ) == 0
    assert os.system(
        """python -m snakemk_util.main --snakefile tests/data/test_rule_args/Snakefile --rule "all" --script_flavor "PythonJupyterNotebook" """
    ) == 0