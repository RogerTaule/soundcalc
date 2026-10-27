# tests/test_stir.py
from soundcalc.pcs.stir import get_STIR_proof_size_bits
from soundcalc.zkvms import dummy_stir


def test_get_STIR_proof_size_bits():
    hash_size_bits = 1
    base_field_bits = 1
    ext_field_bits = 2
    batch_size = 3
    folding_factors = [1, 2]  # f_0 in blocks of 2, f_1 in blocks of 4
    # M = 2 iterations: f_0 (log-degree 4, rate 1/2, domain 32), f_1 (log-degree 3, rate 1/2, domain 16),
    # final polynomial of log-degree 1.
    log_degrees = [4, 3, 1]
    log_inv_rates = [1, 1, 2]
    num_queries = [10, 5]
    num_ood_samples = [2]

    expected = 0
    # roots of the batched functions, f_0 and f_1
    expected += 3 * hash_size_bits
    # OOD answers for f_1
    expected += 2 * ext_field_bits
    # final polynomial: 2^1 coefficients
    expected += 2 * ext_field_bits
    # queries into the batched functions: 32 leaves of 3 base elements; path = leaf + sibling + 4 hashes
    expected += num_queries[0] * (3 * base_field_bits + min(3 * base_field_bits, hash_size_bits) + 4 * hash_size_bits)
    # queries into f_0: 16 leaves of 2 ext elements; path = leaf + sibling + 3 hashes
    expected += num_queries[0] * (2 * ext_field_bits + min(2 * ext_field_bits, hash_size_bits) + 3 * hash_size_bits)
    # queries into f_1: 4 leaves of 4 ext elements; path = leaf + sibling + 1 hash
    expected += num_queries[1] * (4 * ext_field_bits + min(4 * ext_field_bits, hash_size_bits) + 1 * hash_size_bits)

    result = get_STIR_proof_size_bits(
        hash_size_bits,
        base_field_bits,
        ext_field_bits,
        batch_size,
        folding_factors,
        log_degrees,
        log_inv_rates,
        num_queries,
        num_ood_samples,
        False,
    )

    assert result == expected

    # two trees of 2 and 1 base elements instead of one of 3: one more root, smaller leaves
    widths = get_STIR_proof_size_bits(
        hash_size_bits, base_field_bits, ext_field_bits, batch_size, folding_factors, log_degrees,
        log_inv_rates, num_queries, num_ood_samples, False, initial_tree_widths=[2, 1],
    )
    assert widths == result - 10 * (3 + 1 + 4) + 1 + 10 * (2 + 1 + 4) + 10 * (1 + 1 + 4)


def test_dummy_stir_loads_and_reaches_target():
    zkvm = dummy_stir.load()
    circuit = zkvm.get_circuits()[0]
    levels = circuit.get_security_levels()
    assert "UDR" in levels and "JBR" in levels
    assert levels["JBR"]["total"] >= 128
    assert set(levels["JBR"]) >= {"batching", "fold(i=0)", "OOD(i=1)", "shift(i=1)", "fin", "total"}
