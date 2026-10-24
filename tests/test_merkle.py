# tests/test_merkle.py
from itertools import combinations

from soundcalc.common.utils import (
    get_size_of_merkle_multi_proof_bits_expected,
    get_size_of_merkle_multi_proof_bits_worst_case,
)


def _num_siblings(indices, depth):
    """Number of siblings a Merkle multi-proof opening `indices` sends."""
    known, siblings = set(indices), 0
    for _ in range(depth):
        siblings += len({i ^ 1 for i in known} - known)
        known = {i >> 1 for i in known}
    return siblings


def test_worst_case_multi_proof_matches_brute_force():
    # leaves of one element, elements and hashes of one bit: the size is t + the number of siblings.
    # Queries may repeat a leaf, so t queries open any k <= t distinct leaves.
    for depth in range(1, 5):
        for t in range(1, 2**depth + 3):
            worst = max(
                _num_siblings(c, depth)
                for k in range(1, min(t, 2**depth) + 1)
                for c in combinations(range(2**depth), k)
            )
            assert get_size_of_merkle_multi_proof_bits_worst_case(2**depth, t, 1, 1, 1) == t + worst


def test_worst_case_multi_proof_is_at_least_expected():
    for depth in range(1, 11):
        for t in range(1, 3 * 2**depth):
            for tuple_size in (1, 4, 8):
                worst = get_size_of_merkle_multi_proof_bits_worst_case(2**depth, t, tuple_size, 64, 256)
                expected = get_size_of_merkle_multi_proof_bits_expected(2**depth, t, tuple_size, 64, 256)
                assert worst >= expected, (depth, t, tuple_size)
