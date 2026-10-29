from __future__ import annotations

import math

KIB = (1024 * 8) # Kilobytes


def get_rho_plus(H: int, D: float, max_combo: int) -> float:
    """Compute rho+. See page 16 of Ha22"""
    # XXX Should this be (H + 2) / D? This part is cryptic in [Ha22]
    # TODO Figure out
    return (H + max_combo) / D

def get_bits_of_security_from_error(error: float) -> int:
    """
    Returns the maximum k such that error <= 2^{-k}
    """
    return int(math.floor(-math.log2(error)))


def apply_grinding(error: float, grinding_bits: int) -> float:
    """
    Take a soundness error as input, apply `grinding_bits` of grinding and return it.

    Grinding is proof-of-work that the prover performs, reducing the soundness error by a factor of 2^grinding_bits.
    """
    return error * (2 ** (-grinding_bits))


def get_size_of_merkle_multi_proof_bits_expected(num_leafs: int, num_openings: int, tuple_size: int, element_size_bits: int,  hash_size_bits: int) -> int:
    """
    Compute the *expected* size of a Merkle multi-proof in bits.

    We assume a Merkle tree that represents num_leafs leaves.

    Note: the result counts both the leafs and the Merkle path.

    For derivation see: https://xn--2-umb.com/25/merkle-multi-proof/#expected-value-1
    """
    assert num_leafs > 0

    leaf_size = tuple_size * element_size_bits
    leafs_size = num_openings * leaf_size

    tree_depth = math.ceil(math.log2(num_leafs))

    # Round once at the end, not per level, so that it never exceeds the worst case.
    siblings_size = 0
    for d in range(1, tree_depth +1):
        prob_sibling_in_proof = ((1 - 2**(-d))**num_openings - (1 - 2**(1-d))**num_openings)
        # As in a single Merkle path, a sibling leaf is sent instead of its hash if it is smaller.
        sibling_size = min(leaf_size, hash_size_bits) if d == tree_depth else hash_size_bits
        siblings_size += 2**d * prob_sibling_in_proof * sibling_size
    return leafs_size + math.ceil(siblings_size)


def get_size_of_merkle_multi_proof_bits_worst_case(num_leafs: int, num_openings: int, tuple_size: int, element_size_bits: int,  hash_size_bits: int) -> int:
    """
    Compute the *worst case* size of a Merkle multi-proof in bits.

    We assume a Merkle tree that represents num_leafs leaves.

    Note: the result counts both the leafs and the Merkle path.

    Let p_d be the number of nodes at depth d on an opened path (p_0 = 1), and D the tree depth.
    The children of the p_{d-1} path nodes at depth d-1 that are not on a path are sent as
    siblings: 2 p_{d-1} - p_d of them, as hashes above the leaves and as leaves (or their hash,
    if smaller) at the leaves.

    Every path node has a path child, so p_d <= min(2^d, p_{D-1}) for d < D, and p_D >= p_{D-1}.
    Hence, for a fixed j = p_{D-1}:
    - at most j siblings are sent at the leaves, with equality if every path node at depth D-1
      has exactly one opened child;
    - the hashes above the leaves, the sum over d < D of 2 p_{d-1} - p_d, only grow with each
      p_d for d < D-1, so they are largest when p_d = min(2^d, j).
    Opening j leaves spread out as much as possible reaches both bounds, so every opening is at
    most as large as the spread opening with the same j, and we take the max over
    j <= min(t, num_leafs). Note that for a fixed number of opened leaves, spreading them out is
    not always the worst case (two opened sibling leaves can cost less than one hash), but
    closing one of them never makes the proof smaller.
    """
    assert num_leafs > 0

    leaf_size = tuple_size * element_size_bits
    leafs_size = num_openings * leaf_size

    tree_depth = math.ceil(math.log2(num_leafs))

    max_siblings_size = 0
    for j in range(1, min(num_openings, num_leafs) + 1):
        siblings_size = 0
        for d in range(1, tree_depth + 1):
            # With j leaves spread out, min(2^d, j) nodes at depth d are on a path.
            num_siblings = 2 * min(2**(d - 1), j) - min(2**d, j)
            # As in a single Merkle path, a sibling leaf is sent instead of its hash if it is smaller.
            sibling_size = min(leaf_size, hash_size_bits) if d == tree_depth else hash_size_bits
            siblings_size += num_siblings * sibling_size
        max_siblings_size = max(max_siblings_size, siblings_size)
    return leafs_size + max_siblings_size


def get_size_of_merkle_multi_proof_bits(num_leafs: int, num_openings: int, tuple_size: int, element_size_bits: int,  hash_size_bits: int, expected: bool) -> int:
    """
    Compute the *worst case* or *expected* size of a Merkle multi-proof in bits.
    """
    if expected:
        return get_size_of_merkle_multi_proof_bits_expected(num_leafs, num_openings, tuple_size, element_size_bits, hash_size_bits)
    else:
        return get_size_of_merkle_multi_proof_bits_worst_case(num_leafs, num_openings, tuple_size, element_size_bits, hash_size_bits)
