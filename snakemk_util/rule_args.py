import os
from snakemake.workflow import Workflow
from dataclasses import dataclass

@dataclass
class SnakemakeRuleArgs:
    input: dict
    params: dict
    output: dict
    wildcards: dict


class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def load_rule_args(snakefile, rule_name, default_wildcards=None, change_dir=False):
    """
    Returns a rule object for some default arguments.
    Example usage:
        ```
        try:
            snakemake
        except NameError:
            snakefile_path = os.getcwd() + "/Snakefile"

            snakemake = load_rule_args(
                snakefile = snakefile_path,
                rule_name = 'create_prediction_target',
                default_wildcards={
                    'ds_dir': 'full_data_samplefilter'
                }
            )
        ```
    """
    # save current working dir for later
    cwd = os.getcwd()
    try:
        if default_wildcards == None:
            default_wildcards = dict()

        # change to snakefile directory
        os.chdir(os.path.dirname(snakefile))

        # load workflow
        workflow = Workflow(snakefile=snakefile)
        workflow.include(snakefile)
        # get rule
        rule = workflow.get_rule(rule_name)

        smk_input = dict(rule.expand_input(default_wildcards)[0])
        smk_output = dict(rule.expand_output(default_wildcards)[0])
        smk_params = dict(rule.expand_params(
            default_wildcards, rule.input, rule.output, AttrDict(rule.resources)))

        # setup rule arguments
        retval = SnakemakeRuleArgs(
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
