"""Cost calculation utility — compute costs based on token counts and pricing."""


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    input_price_per_1k: float,
    output_price_per_1k: float,
) -> float:
    """
    Calculate cost in CNY based on token counts and per-1K-token prices.

    Args:
        input_tokens: Number of input (prompt) tokens
        output_tokens: Number of output (completion) tokens
        input_price_per_1k: Price per 1K input tokens in CNY
        output_price_per_1k: Price per 1K output tokens in CNY

    Returns:
        Cost in CNY (float, rounded to 6 decimal places)
    """
    input_cost = (input_tokens / 1000.0) * input_price_per_1k
    output_cost = (output_tokens / 1000.0) * output_price_per_1k
    total = input_cost + output_cost
    return round(total, 6)


def format_cost(cost_yuan: float) -> str:
    """Format cost for display in CNY."""
    if cost_yuan < 0.01:
        return f"¥{cost_yuan:.6f}"
    elif cost_yuan < 1:
        return f"¥{cost_yuan:.4f}"
    else:
        return f"¥{cost_yuan:,.2f}"
