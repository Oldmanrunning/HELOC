from pathlib import Path


INPUTS_SOURCE = Path("heloc/ui/inputs.py").read_text()


def test_loan_assumption_inputs_do_not_use_sliders_or_duplicate_exact_field():
    assert "st.slider" not in INPUTS_SOURCE
    assert "Requested draw — exact amount" not in INPUTS_SOURCE
    assert "borrowed_exact" not in INPUTS_SOURCE


def test_requested_draw_number_input_configuration_is_preserved():
    requested_draw_block = INPUTS_SOURCE.split('"Requested HELOC draw (USD)"', maxsplit=1)[1].split(
        ')', maxsplit=1
    )[0]

    assert "min_value=0.0" in requested_draw_block
    assert "value=60000.0" in requested_draw_block
    assert "step=1000.0" in requested_draw_block
    assert 'format="%.2f"' in requested_draw_block


def test_repayment_period_number_input_configuration_is_preserved():
    repayment_period_block = INPUTS_SOURCE.split('"Repayment period (years)"', maxsplit=1)[1].split(
        ')', maxsplit=1
    )[0]

    assert "min_value=1" in repayment_period_block
    assert "max_value=30" in repayment_period_block
    assert "value=15" in repayment_period_block
    assert "step=1" in repayment_period_block
