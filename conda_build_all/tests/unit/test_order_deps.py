import unittest

from conda_build_all.order_deps import resolve_dependencies


class Test_resolve_dependencies(unittest.TestCase):
    def test_example(self):
        deps = resolve_dependencies({'a': ['b', 'c'], 'b': ['c'],
                                     'c': ['d'], 'd': []})
        self.assertEqual(list(deps), ['d', 'c', 'b', 'a'])

    def test_example_different_order(self):
        deps = resolve_dependencies({'a': ['b', 'c'], 'b': ['d'],
                                     'c': ['b'], 'd': []})
        self.assertEqual(list(deps), ['d', 'b', 'c', 'a'])

    def test_unresolvable(self):
        deps = resolve_dependencies({'a': ['b'], 'b': ['a']},
                                    existing_packages=set())
        with self.assertRaises(ValueError):
            list(deps)

    def test_longer_unresolvable_circular(self):
        deps = resolve_dependencies({'a': ['b'], 'b': ['c'], 'c':['a']})
        with self.assertRaises(ValueError):
            list(deps)

    def test_resolvable_circular_a(self):
        deps = resolve_dependencies({'a': ['b'], 'b': ['a']},
                                    existing_packages={'a'})
        self.assertEqual(list(deps), ['b', 'a'])

    def test_resolvable_circular_b(self):
        deps = resolve_dependencies({'a': ['b'], 'b': ['a']},
                                    existing_packages={'b'})
        self.assertEqual(list(deps), ['a', 'b'])

    def test_resolvable_circular_long(self):
        deps = resolve_dependencies({'a':['b'], 'b':['c'], 'c':['a']}, {'c'})
        self.assertEqual(list(deps), ['b', 'a', 'c'])

    # At present I don't know how to guarantee order where it doesn't 'matter'
    '''
    def test_resolvable_circular_ab(self):
        deps = resolve_dependencies({'a': ['b'], 'b': ['a']},
                                    existing_packages={'a', 'b'})
        self.assertEqual(list(deps), ['a', 'b'])
    '''

    def test_missing_link(self):
        deps = resolve_dependencies({'a': ['b'], 'c': ['d']})
        with self.assertRaises(ValueError):
            list(deps)

    def test_resolvable_unlisted(self):
        deps = resolve_dependencies({'a': ['b', 'c'], 'b': ['c']},
                                    existing_packages={'c'})
        self.assertEqual(list(deps), ['b', 'a'])

