def loan_to_value(estimated_loan: float, home_value: float) -> float:
    return (estimated_loan / home_value) if home_value else 0.0
