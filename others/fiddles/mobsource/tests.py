from django.test import TestCase
from .models import dg, ndcg

class nDCGTests(TestCase):

    def test_all_top_scores_results_in_top(self):
        perfect_score = [ 1, 1, 1, 1, 1 ]
        calculated_ndcg = ndcg(perfect_score, items=5, max_score=1)
        self.assertEquals(1.0, calculated_ndcg)

    def test_irrelevant_set_results_in_zero(self):
        lousy_score = [ 0, 0, 0, 0, 0]
        calculated_ndcg = ndcg(lousy_score)
        self.assertEquals(0, calculated_ndcg)

    def test_sane_set_yields_sane_values(self):
        # assuming top relevance score is 5
        test_scores = [5, 4, 3, 2, 1, 0, 1, 2, 3, 4]
        self.assertGreater(ndcg(test_scores), 0)
        self.assertLess(ndcg(test_scores), 1)



