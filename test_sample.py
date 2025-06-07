"""Sample code with various issues for testing EcoGuard AI."""

# import os  # Unused import for testing
# import sys  # Unused import for testing
from typing import Any, List

# import unused_module  # Unused import for testing


def inefficient_function() -> str:
    """This function has several issues."""

    # Inefficient string concatenation in loop
    result = ""
    for i in range(100):
        result = result + str(i) + ", "  # Should trigger green rule

    # Unused variable
    unused_var = "This variable is never used"  # noqa: F841

    return result


def complex_function(a: Any, b: Any, c: Any, d: Any, e: Any, f: Any, g: Any) -> str:
    """Function with high complexity."""
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            if g:
                                return "very nested"
                            else:
                                return "g false"
                        else:
                            return "f false"
                    else:
                        return "e false"
                else:
                    return "d false"
            else:
                return "c false"
        else:
            return "b false"
    else:
        return "a false"


def verbose_check(data: Any) -> bool:
    if data is not None:
        if len(data) > 0:
            return True
        else:
            return False
    else:
        return False


# Range/len anti-pattern
def inefficient_loop(items: List[Any]) -> None:
    for i in range(len(items)):
        print(f"Item {i}: {items[i]}")


# Redundant variable assignment
def redundant_return() -> int:
    result = 42
    return result


# List that could be generator
def could_be_generator() -> int:
    data = [x * 2 for x in range(1000)]
    return sum(data)
