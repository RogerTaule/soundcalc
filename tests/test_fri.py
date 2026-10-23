# tests/test_fri.py
import pytest

from soundcalc.pcs.fri import get_FRI_proof_size_bits
from soundcalc.zkvms import dummy_stir, pico

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

    size_per_query = 0
    size_per_query += 7 * hash_size_bits + 3 * field_size_bits
    size_per_query += 6 * hash_size_bits + 2 * field_size_bits
    size_per_query += 5 * hash_size_bits + 2 * field_size_bits

    expected += 16 * field_size_bits
    expected += num_queries * size_per_query

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
    old, new = 1 + 10 * (6 + 1 + 6), 1 + 10 * (2 + 1 + 6) + 1 + 10 * (1 + 1 + 6)
    assert result == get_FRI_proof_size_bits(*args) - old + new


@pytest.mark.parametrize("zkvm", [pico, dummy_stir])
def test_num_evals_adds_to_proof_size(zkvm):
    pcs = zkvm.load().get_circuits()[0].pcs
    sizes = pcs.get_proof_size_bits(), pcs.get_expected_proof_size_bits()
    pcs.num_evals = 5
    added = 5 * pcs.field.extension_field_element_size_bits()
    assert (pcs.get_proof_size_bits(), pcs.get_expected_proof_size_bits()) == (sizes[0] + added, sizes[1] + added)
