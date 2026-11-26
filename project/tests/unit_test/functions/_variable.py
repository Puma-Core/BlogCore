from profiles.models import Variable


def _variable(**overrides) -> Variable:
    defaults = {
        "identifier": "username",
        "label": "Username",
        "description": "Social network username",
        "regex": r"[A-Za-z0-9_]+",
    }
    defaults.update(overrides)
    return Variable(**defaults)
