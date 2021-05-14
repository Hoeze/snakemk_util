import os
from snakemake.workflow import Workflow
from dataclasses import dataclass

import logging

log = logging.getLogger(__name__)


@dataclass
class SnakemakeRuleArgs:
    resources: dict
    input: dict
    params: dict
    output: dict
    wildcards: dict


class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


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

    if isinstance(path_iterable, list):
        return list(map(lambda x: include_custom_wd(workflow, x, root=root), path_iterable))
    elif isinstance(path_iterable, dict):
        return {k: include_custom_wd(workflow, v, root=root) for k, v in path_iterable.items()}


def load_rule_args(snakefile, rule_name, default_wildcards=None, change_dir=False, create_dir=True, root=None):
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
        ```
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
            default_wildcards = dict()

        # change to root directory
        os.chdir(root)

        # load workflow
        workflow = Workflow(snakefile=snakefile)
        workflow.include(snakefile)
        # get rule
        rule = workflow.get_rule(rule_name)

        smk_resources = AttrDict(rule.resources)
        smk_input = dict(rule.expand_input(default_wildcards)[0])
        smk_output = dict(rule.expand_output(default_wildcards)[0])
        smk_params = dict(rule.expand_params(
            default_wildcards,
            rule.input,
            rule.output,
            smk_resources
        ))

        # Make paths in snakemake inputs and outputs absolute
        smk_input = map_custom_wd(workflow, smk_input, root)
        smk_output = map_custom_wd(workflow, smk_output, root)

        if create_dir:
            if isinstance(smk_output, list):
                path_list = smk_output
            elif isinstance(smk_output, dict):
                path_list = list(smk_output.values())
            else:
                raise ValueError("Unknown output type '%s'" % type(smk_output))

            for path in path_list:
                dest_folder = os.path.join(os.getcwd(), os.path.dirname(path))
                if os.path.isdir(dest_folder):
                    pass
                else:
                    log.info(f"Creating output directory {dest_folder}")
                    os.makedirs(dest_folder)

        # setup rule arguments
        retval = SnakemakeRuleArgs(
            resources=smk_resources,
            input=smk_input,
            params=smk_params,
            output=smk_output,
            wildcards=default_wildcards
        )
        return retval
    finally:
        if not change_dir:
            # change back to previous working directory
            os.chdir(cwd)
