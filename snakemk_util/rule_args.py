import os
import json
import logging
from typing import Dict, List, Literal, Type, Union, overload

# workaround for https://github.com/snakemake/snakemake/issues/2786
import snakemake.cli
from snakemake import script
from snakemake.logging import LoggerManager
from snakemake.rules import (
    InputFiles,
    Namedlist,
    OutputFiles,
    Params,
    Wildcards,
)
from snakemake.settings.types import OutputSettings
from snakemake.workflow import Workflow

try:
    from snakemake import notebook
except ImportError:
    notebook = None

log = logging.getLogger(__name__)


def include_custom_wd(workflow, path, root=None):
    # if path is absolute, leave it
    if os.path.isabs(path):
        return path

    if root is None:
        root = ""

    # Otherwise the path is relative
    if workflow.workdir_init is not None:
        if os.path.isabs(workflow.workdir_init):
            return os.path.join(workflow.workdir_init, path)
        else:
            # Make the path absolute
            # https://github.com/Hoeze/snakemk_util/issues/1
            return os.path.abspath(os.path.join(root, workflow.workdir_init, path))
    else:
        return os.path.abspath(os.path.join(root, path))


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
    if isinstance(path_iterable, Namedlist):
        # Use toclone + custom_map to avoid copying _IOFile objects (snakemake 9)
        return type(path_iterable)(
            toclone=path_iterable,
            custom_map=lambda p: include_custom_wd(workflow, str(p), root=root),
        )
    elif isinstance(path_iterable, list):
        return [map_custom_wd(workflow, item, root=root) for item in path_iterable]
    elif isinstance(path_iterable, dict):
        return {k: map_custom_wd(workflow, v, root=root) for k, v in path_iterable.items()}
    else:
        return include_custom_wd(workflow, str(path_iterable), root=root)


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
    return "Snakemake(" + json.dumps(_pretty_format_smk(snakemake_obj.__dict__), indent=2, default=str) + ")"


@overload
def load_rule_args(
    snakefile: str,
    rule_name: str,
    default_wildcards: Union[Dict[str, str], Wildcards] = ...,
    change_dir: bool = ...,
    create_dir: bool = ...,
    root: str = ...,
    flavor: None = ...,
    add_utility_functions: bool = ...,
) -> script.Snakemake: ...


@overload
def load_rule_args(
    snakefile: str,
    rule_name: str,
    default_wildcards: Union[Dict[str, str], Wildcards] = ...,
    change_dir: bool = ...,
    create_dir: bool = ...,
    root: str = ...,
    flavor: Union[str, Type[script.ScriptBase]] = ...,
    add_utility_functions: bool = ...,
) -> str: ...


def load_rule_args(
    snakefile: str,
    rule_name: str,
    default_wildcards: Union[Dict[str, str], Wildcards] = None,
    change_dir: bool = False,
    create_dir: bool = True,
    root: str = None,
    flavor: Union[str, Type[script.ScriptBase], None] = None,
    add_utility_functions=True,
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
    :param flavor: Script language for which the preamble should be generated.
        If not set, will return a python Snakemake object.
        Examples: 'BashScript', 'JuliaScript', 'PythonScript', 'RMarkdown', 'RScript',
        'RustScript', 'PythonJupyterNotebook', 'RJupyterNotebook'
    :param add_utility_functions: Add a reload function to reload the snakemake object
        by re-executing the workflow for development purposes
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
        if default_wildcards is None:
            default_wildcards = Wildcards()
        elif not isinstance(default_wildcards, Wildcards):
            default_wildcards = Wildcards(fromdict=default_wildcards)

        # change to root directory
        os.chdir(root)

        # load workflow
        workflow = Workflow(
            resource_settings=snakemake.workflow.ResourceSettings(),
            config_settings=snakemake.workflow.ConfigSettings(),
            storage_settings=snakemake.workflow.StorageSettings(),
            workflow_settings=snakemake.workflow.WorkflowSettings(),
            deployment_settings=snakemake.workflow.DeploymentSettings(),
            logger_manager=LoggerManager(
                logging.getLogger("snakemake"),
                OutputSettings(),
            ),
            overwrite_workdir=root,
        )
        workflow.include(snakefile)
        # get rule
        rule = workflow.get_rule(rule_name)

        smk_input = InputFiles(rule.expand_input(default_wildcards)[0])
        smk_resources = rule.expand_resources(default_wildcards, smk_input, attempt=1)
        smk_threads = smk_resources._cores
        smk_output = OutputFiles(rule.expand_output(default_wildcards)[0])
        smk_params = Params(rule.expand_params(default_wildcards, smk_input, smk_output, None))
        smk_log = rule.log
        smk_config = workflow.config

        # Make paths in snakemake inputs and outputs absolute
        smk_input = map_custom_wd(workflow, smk_input, root)
        smk_output = map_custom_wd(workflow, smk_output, root)

        smk_scriptdir = rule.basedir.get_path_or_uri(secret_free=True)

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
                rule.basedir.get_path_or_uri(secret_free=True),
            )
            if add_utility_functions:
                # add function to reload the object for debugging purposes
                retval.reload = lambda: retval.__dict__.update(
                    reload_snakemake(
                        snakefile=snakefile,
                        snakemake_obj=retval,
                        root=root,
                        create_dir=create_dir,
                    ).__dict__
                )

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
                singularity_args=workflow.deployment_settings.apptainer_args,
                env_modules=rule.env_modules,
                bench_record=None,
                jobid=0,
                bench_iteration=None,
                cleanup_scripts=None,
                shadow_dir=None,
                is_local=workflow.is_local(rule),
                runtime_paths=workflow.runtime_paths,
            )

            return script_obj.get_preamble()

    finally:
        if not change_dir:
            # change back to previous working directory
            os.chdir(cwd)


def reload_snakemake(snakefile: str, snakemake_obj: script.Snakemake, create_dir=False, root=None) -> script.Snakemake:
    """
    Reload snakemake object by re-executing the workflow

    :param snakefile: path to the root Snakefile
    :param snakemake_obj: the Snakemake object to reload
    :param create_dir: Create required output folders
    :param root: Root directory from where you would run the `snakemake` command.
      By default, this is the folder that contains the root Snakefile (see the `snakefile` argument).
    """
    return load_rule_args(
        snakefile=snakefile,
        rule_name=snakemake_obj.rule,
        default_wildcards=snakemake_obj.wildcards,
        change_dir=False,
        create_dir=create_dir,
        root=root,
    )
