from typing import Any
from .rules_schema import DerivedIncomeCondition
def apply_numeric_condition(value:float,condition:DerivedIncomeCondition)->bool:
    op = condition.operator
    if op == "equal":
        return value == condition.value
    elif op == "not_equal":
        return value != condition.value
    elif op == "greater_than":
        return value > condition.value
    elif op == "greater_than_or_equal":
        return value >= condition.value
    elif op == "less_than":
        return value < condition.value
    elif op == "less_than_or_equal":
        return value <= condition.value
    elif op == "between":
        return condition.lower <= value <= condition.upper
    else:
        raise ValueError(f"Unsupported operator {op}")