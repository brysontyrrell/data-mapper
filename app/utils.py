from deepdiff import DeepDiff, Delta


def iterdict(d):
    if not isinstance(d, dict):
        return {}

    for k, v in d.items():
        print(k, v)
        if isinstance(v, dict):
            yield from iterdict(v)
        else:
            yield v


def del_null_value_keys(d: dict):
    dc = d.copy()
    for k, v in dc.items():
        if isinstance(v, dict):
            del_null_value_keys(v)
        elif v is None:
            del d[k]


def patch_item(old_item: dict, patch_item: dict):
    # Update a dict using JSON Merge Patch
    # `None` values will result in key removal
    # Lists are overwritten.
    diff = DeepDiff(old_item, patch_item)
    delta = Delta(diff)
    # Keys marked as removed should stay - persisted but not updated
    if delta.diff.get("dictionary_item_removed"):
        del delta.diff["dictionary_item_removed"]

    updated = old_item + delta
    del_null_value_keys(updated)
    return updated
