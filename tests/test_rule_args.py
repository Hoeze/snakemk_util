import pytest
import pandas as pd
import numpy as np
import os
import shutil

from snakemk_util import load_rule_args


@pytest.fixture(scope="function")
def workflow_dir(tmpdir_factory):
    dn = tmpdir_factory.mktemp("workflow_dir")
    path = str(dn)
    shutil.copyfile("tests/data/test_rule_args/Snakefile", path + "/Snakefile")

    return path


def test_rule_args(workflow_dir):
    snakefile_path = workflow_dir + "/Snakefile"

    snakemake = load_rule_args(
        snakefile=snakefile_path,
        rule_name='samplerule',
        default_wildcards={
            'ds_dir': 'testdir'
        }
    )

    assert os.path.isdir(workflow_dir + "/testdir")
