import pytest

from bottex2 import router


def invalid_condition(message):
    return True

def valid_condition(message, **params):
    return True


def test_check_condition():
    router.is_case_valid(valid_condition)
    with pytest.raises(ValueError):
        router.is_case_valid(invalid_condition)
