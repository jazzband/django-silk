def dict_contains(child_dict, parent_dict):
    for key, value in child_dict.items():
        if key not in parent_dict:
            return False
        if parent_dict[key] != value:
            return False
    return True
