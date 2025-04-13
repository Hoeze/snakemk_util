# Snakemake Utility functions for easier working with snakemake

When debugging a script that uses snakemake to define its inputs, it is often difficult to manually set some example inputs for testing.
This utility allows to directly obtain a Snakemake object from the pipeline by specifying the desired rule and wildcards.

## Loading snakemake object without actually running `snakemake`
For obtaining a Snakemake object in python, simply paste the following preamble in your script and adjust `snakefile_path`, `rule_name` and `default_wildcards`.
```python
try:
    snakemake
except NameError:
    import os
    from snakemk_util import load_rule_args, pretty_print_snakemake
    
    snakefile_path = os.getcwd() + "/Snakefile"
    snakemake = load_rule_args(
        snakefile = snakefile_path,
        rule_name = 'create_prediction_target',
        default_wildcards={
            'ds_dir': 'all_data'
        }
    )
    print(pretty_print_snakemake(snakemake))
```
Output:
```python
Snakemake({
  "threads": 64,
  "resources": {
    "_cores": 64,
    "_nodes": 1,
    "tmpdir": "<function DefaultResources.__init__.<locals>.fallback.<locals>.callable at 0x154022f799d0>",
    "ntasks": 1,
    "mem_mb": 250000
  },
  "input": {
    "0": "some_input.csv"
    "config": "some_config.yaml",
  },
  "params": {
    "nb_script": "create_prediction_target.py"
  },
  "output": {
    [...]
  },
  "wildcards": {
    "ds_dir": "all_data"
  },
  "log": [],
  "config": {
    [...]
  },
  "rule": "create_prediction_target"
})
```
- The preamble has no effect during `snakemake` runs, so it can be kept in the script permanently.
- `pretty_print_snakemake` knows about the `NamedList` that snakemake uses and prints all non-named parameters by their index

Here the corresponding snippet for R:
```R
if (! exists("snakemake")) {
    rule = "create_prediction_target"
    python = "/opt/anaconda/envs/snakemake/bin/python"
    wildcards = paste(
        # 'comparison=all',
        sep=','
    )

    cmd=c(
        "-m snakemk_util.main",
        "--rule", rule,
        "--snakefile", normalizePath(snakefile),
        "--root", dirname(normalizePath(snakefile)),
        "--wildcards", paste0('"', wildcards, '"'),
        "--gen-preamble RScript",
        "--create_dirs"
    )
    eval(parse(text=system2(python, cmd, stdout=TRUE, stderr="")))
}
```

## Inspecting the rule parameters on the command line
`snakemk_util` also provides a command-line interface which allows to display the `snakemake` objects for some rule and wildcard as well as generating script preambles for different languages:

```bash
# snakemk_util --help
usage: snakemk_util [-h] --rule RULE_NAME [--gen-preamble FLAVOR] [--snakefile SNAKEFILE] [--root_dir ROOT_DIR] [--wildcards WILDCARDS] [--create_dirs]

Utility to sow Snakemake rule contents and creating script preambles without actually running Snakemake.

optional arguments:
  -h, --help            show this help message and exit
  --rule RULE_NAME      Name of the rule that should be formatted
  --gen-preamble FLAVOR
                        Script language for which the preamble should be generated Examples: 'BashScript', 'JuliaScript', 'PythonScript', 'RMarkdown', 'RScript', 'RustScript', 'PythonJupyterNotebook', 'RJupyterNotebook'
  --snakefile SNAKEFILE
                        path to the Snakefile
  --root_dir ROOT_DIR   Root directory from where you would run the `snakemake` command. By default, this is the current working directory.
  --wildcards WILDCARDS
                        Comma-separated key-value list of wildcards which should be used to format the rule output. Example: 'wildcard0=x,wildcard1=y
  --create_dirs         Create the output directories for the rule
```


## Installation
`pip install snakemk_util`
