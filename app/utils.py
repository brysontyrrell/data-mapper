def iterdict(d):
    if not isinstance(d, dict):
        return {}

    for k, v in d.items():
        print(k, v)
        if isinstance(v, dict):
            yield from iterdict(v)
        else:
            yield v
