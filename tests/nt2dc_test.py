from dataclasses import is_dataclass, fields
from typing import NamedTuple, Tuple, List, FrozenSet, Dict, Type
import sys

import unittest
import nt2dc


class SimpleNamedTuple(NamedTuple):
    a: int
    b: float
    c: bool


class SimpleNameTupleWithGenericTypes(NamedTuple):
    a: int
    b: float
    c: bool
    d: Tuple[int, float, bool]
    e: Dict[str, int]
    f: List[int]


class NamedTupleWithReplacement(NamedTuple):
    a: str
    b: FrozenSet[int]
    c: bool


_ReplaceFrozenSetByList: Dict[Type, Type] = {}

if sys.version_info.major == 3 and sys.version_info.minor >= 9:
    _ReplaceFrozenSetByList.update({frozenset: list})
else:
    _ReplaceFrozenSetByList.update({frozenset: List})


class SimpleNamedTupleTest(unittest.TestCase):
    def test_make_dataclass(self):
        dc = nt2dc.make_dataclass(SimpleNamedTuple)
        self.assertTrue(is_dataclass(dc))

    def test_make_dataclass_fields_a(self):
        dc = nt2dc.make_dataclass(SimpleNamedTuple)
        flds = fields(dc)
        self.assertEqual(flds[0].name, "a")
        self.assertEqual(flds[0].type, int)

    def test_make_dataclass_fields_b(self):
        dc = nt2dc.make_dataclass(SimpleNamedTuple)
        flds = fields(dc)
        self.assertEqual(flds[1].name, "b")
        self.assertEqual(flds[1].type, float)

    def test_make_dataclass_fields_c(self):
        dc = nt2dc.make_dataclass(SimpleNamedTuple)
        flds = fields(dc)
        self.assertEqual(flds[2].name, "c")
        self.assertEqual(flds[2].type, bool)

    def test_convert_instance(self):
        inst: SimpleNamedTuple = SimpleNamedTuple(1, 2.1, True)
        new_inst, _ = nt2dc.get_dataclass_object(inst)
        self.assertEqual(new_inst.a, 1)
        self.assertEqual(new_inst.b, 2.1)
        self.assertEqual(new_inst.c, True)


class NamedTupleWithReplacementTest(unittest.TestCase):

    replace = _ReplaceFrozenSetByList

    def test_make_dataclass(self):
        dc = nt2dc.make_dataclass(NamedTupleWithReplacement)
        self.assertTrue(is_dataclass(dc))

    def test_make_dataclass_replace(self):
        dc = nt2dc.make_dataclass(NamedTupleWithReplacement, self.replace)
        self.assertTrue(is_dataclass(dc))

    def test_make_dataclass_fields_a(self):
        dc = nt2dc.make_dataclass(NamedTupleWithReplacement)
        flds = fields(dc)
        self.assertEqual(flds[0].name, "a")
        self.assertEqual(flds[0].type, str)

    def test_make_dataclass_replace_fields_a(self):
        dc = nt2dc.make_dataclass(NamedTupleWithReplacement, self.replace)
        flds = fields(dc)
        self.assertEqual(flds[0].name, "a")
        self.assertEqual(flds[0].type, str)

    def test_make_dataclass_fields_b(self):
        dc = nt2dc.make_dataclass(NamedTupleWithReplacement)
        flds = fields(dc)
        self.assertEqual(flds[1].name, "b")
        self.assertEqual(flds[1].type, FrozenSet[int])

    def test_make_dataclass_replace_fields_b(self):
        dc = nt2dc.make_dataclass(NamedTupleWithReplacement, self.replace)
        flds = fields(dc)
        self.assertEqual(flds[1].name, "b")
        self.assertEqual(flds[1].type, List[int])

    def test_make_dataclass_fields_c(self):
        dc = nt2dc.make_dataclass(NamedTupleWithReplacement)
        flds = fields(dc)
        self.assertEqual(flds[2].name, "c")
        self.assertEqual(flds[2].type, bool)

    def test_make_dataclass_replace_fields_c(self):
        dc = nt2dc.make_dataclass(NamedTupleWithReplacement, self.replace)
        flds = fields(dc)
        self.assertEqual(flds[2].name, "c")
        self.assertEqual(flds[2].type, bool)

    def test_convert_instance(self):
        fs = frozenset([1, 2, 3])
        inst: NamedTupleWithReplacement = NamedTupleWithReplacement(
            "Hello, World", fs, True
        )
        new_inst, _ = nt2dc.get_dataclass_object(inst)
        self.assertEqual(new_inst.a, "Hello, World")
        self.assertEqual(new_inst.b, fs)
        self.assertNotEqual(new_inst.b, list(fs))
        self.assertEqual(new_inst.c, True)

    def test_convert_instance_replace(self):
        fs = frozenset([1, 2, 3])
        inst: NamedTupleWithReplacement = NamedTupleWithReplacement(
            "Hello, World", fs, True
        )
        new_inst, _ = nt2dc.get_dataclass_object(inst, self.replace)
        self.assertEqual(new_inst.a, "Hello, World")
        self.assertEqual(new_inst.b, list(fs))
        self.assertNotEqual(new_inst.b, fs)
        self.assertEqual(new_inst.c, True)


if __name__ == "__main__":
    unittest.main()
