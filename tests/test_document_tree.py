import unittest

from agentic_tree_rag.document_tree import markdown_to_tree, merge_small_leaves


class DocumentTreeTests(unittest.TestCase):
    def test_markdown_hierarchy_and_text(self) -> None:
        tree = markdown_to_tree("# A\nintro\n## B\ndetail", "sample")
        section_a = tree.children[0]
        self.assertEqual(section_a.title, "A")
        self.assertEqual(section_a.children[0].text, "intro")
        self.assertEqual(section_a.children[1].title, "B")
        self.assertEqual(section_a.children[1].children[0].text, "detail")

    def test_ids_are_deterministic(self) -> None:
        first = markdown_to_tree("# A\ntext", "sample")
        second = markdown_to_tree("# A\ntext", "sample")
        self.assertEqual(
            [node.node_id for node in first.walk()],
            [node.node_id for node in second.walk()],
        )

    def test_merge_adjacent_short_leaves(self) -> None:
        tree = markdown_to_tree("# A\none\n\ntwo", "sample")
        merge_small_leaves(tree, min_chars=10)
        section = tree.children[0]
        self.assertEqual(len(section.children), 1)
        self.assertEqual(section.children[0].text, "one\ntwo")


if __name__ == "__main__":
    unittest.main()
