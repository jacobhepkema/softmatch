import unittest
import os
import tempfile
from softmatch.visualization import generate_html, generate_cluster_html

class TestVisualization(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.output_path = os.path.join(self.test_dir.name, "test.html")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_generate_html_smoke(self):
        data = [
            {
                'id': 'read1',
                'seq': 'ATGCATGC',
                'hits': [
                    {'name': 'A1', 'start': 0, 'end': 4, 'len': 4, 'errors': 0, 'match_seq': 'ATGC', 'strand': 1}
                ]
            }
        ]
        # This should not raise NameError or other exceptions
        generate_html(data, self.output_path)
        self.assertTrue(os.path.exists(self.output_path))

    def test_generate_cluster_html_smoke(self):
        clusters = {
            (('A1', 1),): [
                {
                    'id': 'read1',
                    'seq_len': 8,
                    'hits': [{'name': 'A1', 'start': 0, 'end': 4, 'len': 4, 'errors': 0, 'strand': 1}],
                    'distances': ()
                }
            ]
        }
        # This should not raise exceptions
        generate_cluster_html(clusters, self.output_path)
        self.assertTrue(os.path.exists(self.output_path))

if __name__ == "__main__":
    unittest.main()
