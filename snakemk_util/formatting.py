def recursive_format(data, params, fail_on_unknown=False):
    if isinstance(data, str):
        return data.format(**params)
    elif isinstance(data, dict):
        return {k: recursive_format(v, params, fail_on_unknown=fail_on_unknown) for k, v in data.items()}
    elif isinstance(data, list):
        return [recursive_format(v, params, fail_on_unknown=fail_on_unknown) for v in data]
    else:
        if fail_on_unknown:
            raise ValueError("Handling of data type not implemented: %s" % type(data))
        else:
            return data
