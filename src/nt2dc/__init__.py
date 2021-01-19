"""This module provides methods to convert a named tuple to a data class.
   There is also a set of methods to convert a dataclass back to namedtuple,
   if needed.
"""

from .named_tuple import make_dataclass, get_dataclass_object
from .dataclass import namedtuple, get_named_tuple_object

__all__ = [
    "make_dataclass",
    "get_dataclass_object",
    "namedtuple",
    "get_named_tuple_object",
]
