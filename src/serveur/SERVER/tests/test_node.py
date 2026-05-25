import os
import sys
import unittest


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ALGO.node import Node


class TestNode(unittest.TestCase):
    def test_get_best_move_child_returns_none_without_children(self):
        root = Node(None, None, 0)

        self.assertIsNone(root.get_best_move_child())

    def test_get_best_move_child_prefers_higher_visit_count(self):
        root = Node(None, None, 0)
        first_child = Node(root, "first", 1)
        first_child.visit_count = 3
        first_child.value = 3
        second_child = Node(root, "second", 1)
        second_child.visit_count = 5
        second_child.value = 1
        root.children = [first_child, second_child]

        self.assertIs(root.get_best_move_child(), second_child)

    def test_get_best_move_child_breaks_visit_ties_with_parent_perspective(self):
        root = Node(None, None, 0)
        first_child = Node(root, "first", 1)
        first_child.visit_count = 4
        first_child.value = 2
        second_child = Node(root, "second", 1)
        second_child.visit_count = 4
        second_child.value = 3
        root.children = [first_child, second_child]

        self.assertIs(root.get_best_move_child(), second_child)

    def test_select_best_child_maximizes_on_ai_turn(self):
        root = Node(None, None, 0)
        root.visit_count = 10
        first_child = Node(root, "first", 1)
        first_child.visit_count = 4
        first_child.value = 2
        first_child.prior = 0.0
        second_child = Node(root, "second", 1)
        second_child.visit_count = 4
        second_child.value = 3
        second_child.prior = 0.0
        root.children = [first_child, second_child]

        self.assertIs(root.select_best_child(maximize=True), second_child)

    def test_select_best_child_minimizes_on_opponent_turn(self):
        root = Node(None, None, 1)
        root.visit_count = 10
        first_child = Node(root, "first", 0)
        first_child.visit_count = 4
        first_child.value = 2
        first_child.prior = 0.0
        second_child = Node(root, "second", 0)
        second_child.visit_count = 4
        second_child.value = 3
        second_child.prior = 0.0
        root.children = [first_child, second_child]

        self.assertIs(root.select_best_child(maximize=False), first_child)


if __name__ == "__main__":
    unittest.main()