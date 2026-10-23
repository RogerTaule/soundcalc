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
        batch_size,
        num_queries,
        domain_size,
        folding_factors,
        rate,
        False
    )

    assert result == expected
