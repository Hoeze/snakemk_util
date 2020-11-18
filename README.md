# Snakemake utils
Utility functions for snakemake

## Examples
### Loading snakemake object without actually running `snakemake`
```python
try:
    snakemake
except NameError:
    from snakemk_util import load_rule_args
    
    snakefile_path = os.getcwd() + "/Snakefile"
    snakemake = load_rule_args(
        snakefile = snakefile_path,
        rule_name = 'create_prediction_target',
        default_wildcards={
            'ds_dir': 'all_data'
        }
    )
```

## Installation
`pip install snakemk_util`
