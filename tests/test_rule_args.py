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

    return path


def copy_data(workflow_dir, data_subdir):
    target_dirname = os.path.join(workflow_dir, data_subdir)
    shutil.copytree(f"tests/data/{data_subdir}", target_dirname)
    return target_dirname


def test_rule_args(workflow_dir):
    workflow_dir = copy_data(workflow_dir, "test_rule_args")

    snakefile_path = workflow_dir + "/Snakefile"

    snakemake = load_rule_args(
        snakefile=snakefile_path,
        rule_name='samplerule',
        default_wildcards={
            'ds_dir': 'testdir'
        },
    )

    assert os.path.isdir(workflow_dir + "/testdir")


def test_rule_args_workdir(workflow_dir):
    workflow_dir = copy_data(workflow_dir, "test_rule_args_workdir")

    snakefile_path = workflow_dir + "/workflow/Snakefile"

    snakemake = load_rule_args(
        snakefile=snakefile_path,
        rule_name='samplerule',
        default_wildcards={
        },
        root="../"
    )

    assert os.path.isdir(workflow_dir + "/testdir")
