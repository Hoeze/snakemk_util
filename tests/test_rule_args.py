import pytest
import pandas as pd
import numpy as np
import os
import shutil
import json

from snakemk_util import load_rule_args, pretty_print_snakemake


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

    print(pretty_print_snakemake(snakemake))

    assert os.path.isdir(workflow_dir + "/testdir")


def test_reload(workflow_dir):
    workflow_dir = copy_data(workflow_dir, "test_rule_args")

    snakefile_path = workflow_dir + "/Snakefile"

    snakemake = load_rule_args(
        snakefile=snakefile_path,
        rule_name='samplerule',
        default_wildcards={
            'ds_dir': 'testdir'
        },
    )

    import re

    # replacing function addresses
    find = r'''("<.* at 0x).*>"'''
    replace = r'''\g<1>...>"'''

    x = pretty_print_snakemake(snakemake)
    x = re.sub(find, replace, x)

    print(x)
    snakemake.reload()
    y = pretty_print_snakemake(snakemake)
    y = re.sub(find, replace, y)
    print(y)

    assert x == y


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

    pretty_print_snakemake(snakemake)

    assert os.path.isdir(workflow_dir + "/testdir")


def test_rule_args_workdir_pythonrule(workflow_dir):
    workflow_dir = copy_data(workflow_dir, "test_rule_args_workdir")

    snakefile_path = workflow_dir + "/workflow/Snakefile"

    snakemake = load_rule_args(
        snakefile=snakefile_path,
        rule_name='pythonrule',
        default_wildcards={
        },
        root="../"
    )

    pretty_print_snakemake(snakemake)

    assert os.path.isdir(workflow_dir + "/testdir")


def test_output_args(workflow_dir):
    workflow_dir = copy_data(workflow_dir, "test_output_args")

    snakefile_path = workflow_dir + "/Snakefile"

    snakemake = load_rule_args(
        snakefile=snakefile_path,
        rule_name='samplerule',
        default_wildcards={
            'ds_dir': 'testdir'
        },
    )

    pretty_print_snakemake(snakemake)
