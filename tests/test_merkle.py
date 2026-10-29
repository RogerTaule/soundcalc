# tests/test_merkle.py
from itertools import combinations

from soundcalc.common.utils import (
    get_size_of_merkle_multi_proof_bits_expected,
    get_size_of_merkle_multi_proof_bits_worst_case,
)


def _siblings_size(indices, depth, leaf_size, hash_size):
    """Size of the siblings a Merkle multi-proof opening `indices` sends."""
    known, size = set(indices), 0
    for d in range(depth, 0, -1):
        sibling_size = min(leaf_size, hash_size) if d == depth else hash_size
        size += len({i ^ 1 for i in known} - known) * sibling_size
        known = {i >> 1 for i in known}
    return size


def test_worst_case_multi_proof_matches_brute_force():
    # Queries may repeat a leaf, so t queries open any k <= t distinct leaves. Leaves smaller than
    # half a hash are included: then spreading out a fixed number of leaves is not the worst case.
    for depth in range(1, 5):
        for t in range(1, 2**depth + 3):
            for leaf_size, hash_size in [(1, 1), (1, 4), (3, 4), (4, 1)]:
                worst = max(
                    _siblings_size(c, depth, leaf_size, hash_size)
                    for k in range(1, min(t, 2**depth) + 1)
                    for c in combinations(range(2**depth), k)
                )
                result = get_size_of_merkle_multi_proof_bits_worst_case(2**depth, t, leaf_size, 1, hash_size)
                assert result == t * leaf_size + worst


def test_worst_case_multi_proof_is_at_least_expected():
    for depth in range(1, 11):
        for t in range(1, 3 * 2**depth):
            for tuple_size in (1, 4, 8):
                worst = get_size_of_merkle_multi_proof_bits_worst_case(2**depth, t, tuple_size, 64, 256)
                expected = get_size_of_merkle_multi_proof_bits_expected(2**depth, t, tuple_size, 64, 256)
                assert worst >= expected, (depth, t, tuple_size)
