from unittest import TestCase
from py_tag2domain.util import calc_changes


class UtilTests(TestCase):
    def test_calc_changes(self):
        from_ = set([82, 71])
        to = set([102, 71])
        changes = calc_changes(from_, to)

        self.assertSetEqual(set(changes['insert']), set([102, ]))
        self.assertSetEqual(set(changes['prolong']), set([71, ]))
        self.assertSetEqual(set(changes['end']), set([82, ]))
