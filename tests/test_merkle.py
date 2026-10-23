# tests/test_merkle.py
from itertools import combinations

from soundcalc.common.utils import get_size_of_merkle_multi_proof_bits_worst_case


def _num_siblings(indices, depth):
    """Number of siblings a Merkle multi-proof opening `indices` sends."""
    known, siblings = set(indices), 0
    for _ in range(depth):
        siblings += len({i ^ 1 for i in known} - known)
        known = {i >> 1 for i in known}
    return siblings


def test_worst_case_multi_proof_matches_brute_force():
    # leaves of one element, elements and hashes of one bit: the size is t + the number of siblings
    for depth in range(1, 5):
        for t in range(1, 2**depth + 1):
            worst = max(_num_siblings(c, depth) for c in combinations(range(2**depth), t))
            assert get_size_of_merkle_multi_proof_bits_worst_case(2**depth, t, 1, 1, 1) == t + worst
