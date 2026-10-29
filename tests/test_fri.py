# tests/test_fri.py
from soundcalc.pcs.fri import get_FRI_proof_size_bits

def test_get_FRI_proof_size_bits():
    hash_size_bits = 1
    field_size_bits = 1
    batch_size = 3
    num_queries = 10
    rate = 1/2
    domain_size = 64 * 2
    folding_factors = [2, 2]

    expected = 0
    expected += 3 * hash_size_bits

    # Worst case multi-proofs of 10 openings: no siblings at depth d while 2^d <= 10,
    # 16 - 10 = 6 at depth 4, and 10 at every depth below.
    expected += 10 * 3 * field_size_bits + (6 + 10 + 10 + 10) * hash_size_bits  # 128 leaves
    expected += 10 * 2 * field_size_bits + (6 + 10 + 10) * hash_size_bits  # 64 leaves
    expected += 10 * 2 * field_size_bits + (6 + 10) * hash_size_bits  # 32 leaves

    expected += 16 * field_size_bits

    result = get_FRI_proof_size_bits(
        hash_size_bits,
        field_size_bits,
        1,
        batch_size,
        num_queries,
        domain_size,
        folding_factors,
        rate,
        False
    )

    assert result == expected



def test_get_FRI_proof_size_bits_initial_tree_widths():
    args = (1, 2, 1, 3, 10, 64 * 2, [2, 2], 1 / 2, False)
    result = get_FRI_proof_size_bits(*args, initial_tree_widths=[2, 1])
    # one root and 128 leaves of 3 ext elements -> two roots and 128 leaves of 2 and of 1 base elements
    # Each tree's worst case multi-proof of 10 openings sends 6 + 10 + 10 + 10 siblings, as above.
    siblings = 6 + 10 + 10 + 10
    old, new = 1 + 10 * 6 + siblings, 1 + 10 * 2 + siblings + 1 + 10 * 1 + siblings
    assert result == get_FRI_proof_size_bits(*args) - old + new
