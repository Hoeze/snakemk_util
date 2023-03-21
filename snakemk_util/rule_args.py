import os
from typing import Union, List, Dict, Type

from snakemake.workflow import Workflow
from snakemake.io import Namedlist
from snakemake import script

try:
    from snakemake import notebook
except ImportError:
    notebook = None

# from dataclasses import dataclass

import copy
import json

import logging

log = logging.getLogger(__name__)


# @dataclass
# class SnakemakeRuleArgs:
#     threads: int
#     resources: dict
#     input: dict
#     params: dict
#     output: dict
#     wildcards: dict
#     log: str
#     config: dict
#     rule: str
#
#
# class AttrDict(dict):
#     __getattr__ = dict.__getitem__
#     __setattr__ = dict.__setitem__


def include_custom_wd(workflow, path, root=None):
    # if path is absolute, leave it
    if os.path.isabs(path):
        return path

    if root is None:
        root = ""

    # Otherwise the path is relative
    if workflow._workdir is not None:
        if os.path.isabs(workflow._workdir):
            return os.path.join(workflow._workdir, path)
        else:
            # Make the path absolute
            # https://github.com/Hoeze/snakemk_util/issues/1
            return os.path.abspath(
                os.path.join(root, workflow._workdir, path)
            )
    else:
        return os.path.abspath(
            os.path.join(root, path)
        )


def map_custom_wd(workflow, path_iterable, root=None):
    """
    Make paths relative to the Snakemake working dir absolute

    * If a path is absolute, it is left unchanged
    * If it is relative, assume it is made absolute by
    prepending the root dir and the Snakemake workdir

    ex: `y_KCs_1/edgeR` becomes `/Projects/SCS/` + `results/20201118` + `y_KCs_1/edgeR`

    This makes certain operations straightforward while avoiding hardcoding absolute paths
    in Snakefiles (just on the call to this function)
    """
    # make sure that we keep the object type and only replace the paths
    path_iterable = copy.copy(path_iterable)

    if isinstance(path_iterable, list):
        for i in range(len(path_iterable)):
            path_iterable[i] = map_custom_wd(workflow, path_iterable[i], root=root)
        return path_iterable
    elif isinstance(path_iterable, dict):
        for k in path_iterable.keys():
            path_iterable[k] = map_custom_wd(workflow, path_iterable[k], root=root)
        return path_iterable
    else:
        return include_custom_wd(workflow, path_iterable, root=root)


def mk_dirs(paths: Union[str, List, Dict]):
    if isinstance(paths, list):
        for p in paths:
            mk_dirs(p)
    elif isinstance(paths, dict):
        for p in paths.values():
            mk_dirs(p)
    else:
        dest_folder = os.path.join(os.getcwd(), os.path.dirname(paths))
        if os.path.isdir(dest_folder):
            pass
        else:
            log.info(f"Creating output directory {dest_folder}")
            os.makedirs(dest_folder)


def _pretty_format_smk(snakemake_obj):
    if isinstance(snakemake_obj, Namedlist):
        # directly build string representation
        retval = {}
        for i, (k, v) in enumerate(snakemake_obj._allitems()):
            if k is None:
                assert i not in retval, f"{i} is already a key in '{snakemake_obj}'!"
                retval[i] = _pretty_format_smk(v)
            else:
                retval[k] = _pretty_format_smk(v)
        return retval
    elif isinstance(snakemake_obj, dict):
        return {k: _pretty_format_smk(v) for k, v in snakemake_obj.items()}
    elif isinstance(snakemake_obj, list):
        return [_pretty_format_smk(i) for i in snakemake_obj]
    else:
        return snakemake_obj


def pretty_print_snakemake(snakemake_obj):
    """
    Pretty-print a snakemake object for better inspection of its contents
    """
    return (
            "Snakemake("
            + json.dumps(_pretty_format_smk(snakemake_obj.__dict__), indent=2, default=str)
            + ")"
    )


def load_rule_args(
        snakefile: str,
        rule_name: str,
        default_wildcards: Dict[str, str] = None,
        change_dir: bool = False,
        create_dir: bool = True,
        root: str = None,
        flavor: Union[str, Type[script.ScriptBase]] = None,
) -> Union[str, script.Snakemake]:
    """
    Returns a rule object for some default arguments.
    Example usage:
        ```
        snakefile_path = os.getcwd() + "/Snakefile"

        try:
            snakemake
        except NameError:
            snakemake = load_rule_args(
                snakefile = snakefile_path,
                rule_name = 'create_prediction_target',
                default_wildcards={
                    'ds_dir': 'full_data_samplefilter'
                },
                # root = "./" # path relative to snakefile
            )

        # uncomment this to reload the Snakemake object after editing the rule input/output/params
        # snakemake.reload()
        ```

    :param snakefile: path to the root Snakefile
    :param rule_name: name of the rule
    :param default_wildcards: wildcards in the rule output which are required to format all paths
    :param change_dir: set working directory to the Snakefile root dir
    :param create_dir: Create required output folders
    :param root: Root directory from where you would run the `snakemake` command.
      By default, this is the folder that contains the root Snakefile (see the `snakefile` argument).
    :param flavor: Script language for which the preamble should be generated. If not set, will return a python Snakemake object.
        Examples: 'BashScript', 'JuliaScript', 'PythonScript', 'RMarkdown', 'RScript', 'RustScript', 'PythonJupyterNotebook', 'RJupyterNotebook'
    """
    # save current working dir for later
    cwd = os.getcwd()

    if root is None:
        root = os.path.dirname(snakefile)
    else:
        if not os.path.isabs(root):
            root = os.path.join(os.path.dirname(snakefile), root)

    log.info("root dir: %s", root)

    try:
        if default_wildcards == None:
            default_wildcards = Namedlist()
        elif not isinstance(default_wildcards, Namedlist):
            default_wildcards = Namedlist(fromdict=default_wildcards)

        # change to root directory
        os.chdir(root)

        # load workflow
        workflow = Workflow(snakefile=snakefile)
        workflow.include(snakefile)
        # get rule
        rule = workflow.get_rule(rule_name)

        smk_input = rule.expand_input(default_wildcards)[0]
        smk_resources = rule.expand_resources(default_wildcards, smk_input, attempt=1)
        smk_threads = smk_resources._cores
        smk_output = rule.expand_output(default_wildcards)[0]
        smk_params = rule.expand_params(
            default_wildcards,
            rule.input,
            rule.output,
            smk_resources
        )
        smk_log = rule.log
        smk_config = workflow.config

        # Make paths in snakemake inputs and outputs absolute
        smk_input = map_custom_wd(workflow, smk_input, root)
        smk_output = map_custom_wd(workflow, smk_output, root)

        smk_scriptdir = rule.basedir.get_path_or_uri()

        if create_dir:
            mk_dirs(smk_output)

        # setup rule arguments
        if flavor is None:
            retval = script.Snakemake(
                smk_input,
                smk_output,
                smk_params,
                default_wildcards,
                smk_threads,
                smk_resources,
                smk_log,
                smk_config,
                rule_name,
                None,
                rule.basedir.get_path_or_uri(),
            )
            # add function to reload the object for debugging purposes
            retval.reload = lambda: retval.__dict__.update(reload_snakemake(
                snakefile=snakefile,
                snakemake_obj=retval,
                root=root,
            ).__dict__)

            return retval
        else:  # create script preamble and return as string
            if isinstance(flavor, str):
                if hasattr(script, flavor):
                    flavor: Type[script.ScriptBase] = getattr(script, flavor)
                elif hasattr(notebook, flavor):
                    flavor: Type[script.ScriptBase] = getattr(notebook, flavor)

            # check correct type of `flavor`
            if not isinstance(flavor, type) or not issubclass(flavor, script.ScriptBase):
                raise ValueError(f"Unknown script type specified: '{flavor}'. ")

            script_obj = flavor(
                path=rule.basedir.join(os.path.basename(rule.snakefile)),
                cache_path=None,
                source="",
                basedir=smk_scriptdir,
                input_=smk_input,
                output=smk_output,
                params=smk_params,
                wildcards=default_wildcards,
                threads=smk_threads,
                resources=smk_resources,
                log=smk_log,
                config=smk_config,
                rulename=rule_name,
                conda_env=rule.conda_env,
                conda_base_path=workflow.conda_base_path,
                container_img=rule.container_img,
                singularity_args=workflow.singularity_args,
                env_modules=rule.env_modules,
                bench_record=None,
                jobid=0,
                bench_iteration=None,
                cleanup_scripts=None,
                shadow_dir=None,
                is_local=workflow.is_local(rule)
            )

            return script_obj.get_preamble()

    finally:
        if not change_dir:
            # change back to previous working directory
            os.chdir(cwd)


def reload_snakemake(snakefile: str, snakemake_obj: script.Snakemake, root=None) -> script.Snakemake:
    """
    Reload snakemake object by re-executing the workflow

    :param snakefile: path to the root Snakefile
    :param rule_name: name of the rule
    :param default_wildcards: wildcards in the rule output which are required to format all paths
    :param change_dir: set working directory to the Snakefile root dir
    :param create_dir: Create required output folders
    :param root: Root directory from where you would run the `snakemake` command.
      By default, this is the folder that contains the root Snakefile (see the `snakefile` argument).
    """
    return load_rule_args(
        snakefile=snakefile,
        rule_name=snakemake_obj.rule,
        default_wildcards=snakemake_obj.wildcards,
        change_dir=False,
        create_dir=False,
        root=root,
    )
