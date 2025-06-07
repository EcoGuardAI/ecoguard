"""Sample code with various issues for testing EcoGuard AI."""

import os
import sys
import unused_module  # This should trigger unused import

def inefficient_function():
    """This function has several issues."""
    
    # Inefficient string concatenation in loop
    result = ""
    for i in range(100):
        result = result + str(i) + ", "  # Should trigger green rule
    
    # Unused variable
    unused_var = "This variable is never used"
    
    return result

def complex_function(a, b, c, d, e, f, g):  # Too many parameters
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

# Verbose AI-generated pattern
def verbose_check(data):
    if data is not None:
        if len(data) > 0:
            return True
        else:
            return False
    else:
        return False

# Range/len anti-pattern
def inefficient_loop(items):
    for i in range(len(items)):
        print(f"Item {i}: {items[i]}")

# Redundant variable assignment
def redundant_return():
    result = 42
    return result

# List that could be generator
def could_be_generator():
    data = [x * 2 for x in range(1000)]
    return sum(data)
