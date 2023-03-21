import os

import argparse
import re
import sys
import textwrap
from contextlib import redirect_stdout


def main():
    parser = argparse.ArgumentParser(description=textwrap.dedent("""
    Utility to sow Snakemake rule contents and creating script preambles without actually running Snakemake. 
    """))
    parser.add_argument(
        "--rule",
        action="store",
        dest="rule_name",
        required=True,
        help="Name of the rule that should be formatted",
    )
    parser.add_argument(
        "--gen-preamble",
        action="store",
        dest="flavor",
        default=None,
        help=textwrap.dedent("""
        Script language for which the preamble should be generated
        Examples: 'BashScript', 'JuliaScript', 'PythonScript', 'RMarkdown', 'RScript', 'RustScript', 'PythonJupyterNotebook', 'RJupyterNotebook'
        """),
    )
    parser.add_argument(
        "--snakefile",
        action="store",
        dest="snakefile",
        default="Snakefile",
        help="path to the Snakefile",
    )
    parser.add_argument(
        "--root_dir",
        action="store",
        dest="root_dir",
        default=os.getcwd(),
        help="Root directory from where you would run the `snakemake` command. By default, this is the current working directory.",
    )
    parser.add_argument(
        "--wildcards",
        action="store",
        dest="wildcards",
        default="",
        help="Comma-separated key-value list of wildcards which should be used to format the rule output. Example: 'wildcard0=x,wildcard1=y",
    )
    parser.add_argument(
        "--create_dirs",
        action="store_true",
        dest="create_dirs",
        default=False,
        help="Create the output directories for the rule",
    )
    args = parser.parse_args()

    from snakemk_util.rule_args import load_rule_args, pretty_print_snakemake

    # parse wildcards
    wildcard_pattern = r'([^=,]+)=([^,]*)'
    wildcards = dict(re.findall(wildcard_pattern, args.wildcards))

    with redirect_stdout(sys.stderr):
        snakemake_obj = load_rule_args(
            snakefile=args.snakefile,
            rule_name=args.rule_name,
            default_wildcards=wildcards,
            change_dir=False,
            create_dir=args.create_dirs,
            root=args.root_dir,
            flavor=args.flavor,
            add_utility_functions=False,
        )

    if args.flavor is None:
        print(pretty_print_snakemake(snakemake_obj))
    else:
        print(snakemake_obj)


if __name__ == "__main__":
    main()
