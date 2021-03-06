#
# Copyright (c) 2021 Carsten Igel.
#
# This file is part of nt2dc
# (see https://github.com/carstencodes/nt2dc).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
""" Provides methods to convert a typed named tuple to a dataclass.
"""

from typing import (
    FrozenSet,
    Optional,
    Set,
    Mapping,
    Type,
    NamedTuple,
    Tuple,
    List,
    Any,
    Dict,
    get_type_hints,
    get_args,
    get_origin,
)
from dataclasses import make_dataclass as make_real_dataclass
from collections.abc import Iterable
from sys import version_info as python_version
from importlib import import_module

from .builtins import BuiltInReplacements, BuiltInNames


__BUILT_IN_REPLACEMENTS__ = None
if python_version.major == 3 and python_version.minor < 9:
    __BUILT_IN_REPLACEMENTS__ = BuiltInReplacements

__BUILT_IN_CONSTRUCTORS__ = {
    List: list,
    Dict: dict,
    Set: set,
    FrozenSet: frozenset,
    Tuple: tuple,
}


_type_cache: Dict[Type, Type] = {}


def clear_cache() -> None:
    """Clears the cache of generated classes.
    """
    _type_cache.clear()


def _get_from_cache(clz: Type) -> Optional[Type]:
    if clz in _type_cache.keys():
        return _type_cache[clz]

    return None


def make_dataclass(
    clz: Type[NamedTuple],
    generic_type_mapping: Mapping[Type, Type] = __BUILT_IN_REPLACEMENTS__,
    *,
    prefix: str = "",
    suffix: str = "DataClass",
    use_cache: bool = False,
) -> Type[object]:
    """Creates a dataclass from the specified named tuple.

    Args:
        clz (Type[NamedTuple]): The type to create a dataclass from.
        generic_type_mapping (Mapping[Type, Type], optional): An
            optional mapping of source types to target types, e.g. from set
            to list. Defaults to None.

    Returns:
        Type[object]: The dataclass.
    """
    if use_cache:
        result: Type = _get_from_cache(clz)
        if result is not None:
            return result
    type_hints: List[Tuple[str, Type]] = []
    for key, value in get_type_hints(clz).items():
        value = _get_target_data_type_dc(value, generic_type_mapping)
        type_hints.append((key, value))

    target_name: str = "{}{}{}".format(prefix, clz.__name__, suffix)
    result_class: Type = make_real_dataclass(target_name, type_hints)
    setattr(result_class, "__nt_as_dc", True)
    if use_cache:
        _type_cache[clz] = result_class
    return result_class


def _get_target_data_type_dc(
    value: Type,
    generic_type_mapping: Mapping[Type, Type] = None,
    *,
    prefix: str = "",
    suffix: str = "",
    use_cache: bool = False,
) -> Type:
    args: Tuple = get_args(value)
    if len(args) > 0:
        items: List[Type] = []
        for arg in args:
            arg = _get_target_data_type_dc(
                arg,
                generic_type_mapping,
                prefix=prefix,
                suffix=suffix,
                use_cache=use_cache,
            )
            items.append(arg)

        origin: Type = get_origin(value)
        if (
            generic_type_mapping is not None
            and origin in generic_type_mapping.keys()
        ):
            origin = generic_type_mapping[origin]
        origin = _get_target_data_type_dc(
            origin,
            generic_type_mapping,
            prefix=prefix,
            suffix=suffix,
            use_cache=use_cache,
        )
        value = _make_generic_type(
            origin,
            items,
            generic_type_mapping=generic_type_mapping,
            prefix=prefix,
            suffix=suffix,
            use_cache=use_cache,
        )
    elif _is_namedtuple_class(value):
        value = make_dataclass(
            value,
            generic_type_mapping,
            prefix=prefix,
            suffix=suffix,
            use_cache=use_cache,
        )

    return value


def _make_generic_type(
    generic_base: Type,
    generic_args: List[Type],
    *,
    generic_type_mapping: Mapping[Type, Type] = None,
    prefix: str = "",
    suffix: str = "",
    use_cache: bool = False,
) -> Type:
    _globals: Dict[str, Any] = {}

    def get_module(module_name: str) -> Optional[Any]:
        if len(module_name) == 0:
            return None

        module: Any = import_module(module_name)
        _globals[module_name] = module
        recurse_module_name: str = ""
        if hasattr(module, "__module__"):
            recurse_module_name = module.__module__
        elif hasattr(module, "__package__"):
            recurse_module_name = module.__package__

        if len(recurse_module_name) > 0 and recurse_module_name != module_name:
            _ = get_module(recurse_module_name)

        return module

    def qualname(queried_type) -> str:
        if hasattr(queried_type, "__nt_as_dc") and bool(
            getattr(queried_type, "__nt_as_dc")
        ):
            _globals[queried_type.__name__] = queried_type
            return queried_type.__name__

        prefix: str = ""
        if hasattr(queried_type, "__module__"):
            module: Optional[Any] = get_module(queried_type.__module__)
            if module is not None:
                prefix = "{}.".format(module.__name__)
        if queried_type in BuiltInNames.keys():
            return BuiltInNames[queried_type]

        if hasattr(queried_type, "__qualname__"):
            return prefix + queried_type.__qualname__

        if hasattr(queried_type, "__name__"):
            return prefix + queried_type.__name__

        return str(queried_type)

    base_type_name: str = qualname(generic_base)
    generic_args_dc: List[Type] = [
        _get_target_data_type_dc(
            t,
            generic_type_mapping,
            prefix=prefix,
            suffix=suffix,
            use_cache=use_cache,
        )
        for t in generic_args
    ]
    generic_arg_names: List[str] = [qualname(t) for t in generic_args_dc]
    generic_arg_names_value = ", ".join(generic_arg_names)
    target_type_qualified_name = "{}[{}]".format(
        base_type_name, generic_arg_names_value
    )

    # At this stage, there is no other way than using an eval statement
    # with a qualified name like list[int] or typing.Dict[str, str]
    # pylint: disable=W0123
    result: Type = eval(target_type_qualified_name, _globals)
    return result


def get_dataclass_object(
    instance: NamedTuple,
    generic_type_mapping: Mapping[Type, Type] = __BUILT_IN_REPLACEMENTS__,
    *,
    use_cache: bool = False,
) -> Tuple[object, Type[object]]:
    """Creates a dataclass object from the specified named tuple instance.

    Args:
        instance (NamedTuple): The instance to create a dataclass instance
            from.
        generic_type_mapping (Mapping[Type, Type], optional): An
            optional mapping of source types to target types, e.g. from set
            to list. Defaults to None.
    Returns:
        Tuple[object, Type[object]]: The converted instance and its new type.
    """
    target_type: Type[object] = make_dataclass(
        instance.__class__, generic_type_mapping, use_cache=use_cache
    )
    items_narrowed: Dict[str, Any] = _narrow_named_tuple_instance(
        instance, generic_type_mapping
    )
    new_instance: object = target_type(**items_narrowed)

    return (new_instance, target_type)


def _narrow_named_tuple_instance(
    instance: Any,
    generic_type_mapping: Mapping[Type, Type] = __BUILT_IN_REPLACEMENTS__,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in instance._asdict().items():
        key_type: Type = type(value)
        if value is NamedTuple:
            value = _narrow_named_tuple_instance(value, generic_type_mapping)
        elif value is Iterable:
            items = {v is NamedTuple for v in value}
            if True in items:
                narrowed_items = []
                for item in value:
                    narrowed_items.append(
                        _narrow_named_tuple_instance(
                            item, generic_type_mapping
                        )
                    )

                value = narrowed_items

        if (
            generic_type_mapping is not None
            and key_type in generic_type_mapping.keys()
        ):
            target_type: Type = generic_type_mapping[key_type]
            ctor = target_type
            if target_type in __BUILT_IN_CONSTRUCTORS__.keys():
                ctor = __BUILT_IN_CONSTRUCTORS__[target_type]
            value = ctor(value)

        result[key] = value

    return result


def _is_namedtuple_class(clz: Type) -> bool:
    clz_fields: Dict[str, Any] = clz.__dict__
    has_asdict_method: bool = "_asdict" in clz_fields.keys()
    has_fields_class_member: bool = "_fields" in clz_fields.keys()
    return has_asdict_method and has_fields_class_member


def _is_namedtuple_instance(obj: Any) -> bool:
    is_tuple: bool = isinstance(obj, tuple)

    return is_tuple and _is_namedtuple_class(obj.__class__)
