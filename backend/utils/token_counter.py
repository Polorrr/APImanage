"""Token counting utility — estimates tokens for different model families."""
import re


def estimate_tokens(model_name: str, text: str) -> int:
    """
    Estimate token count for a given model and text.
    - OpenAI models: use tiktoken cl100k_base
    - Chinese-heavy models (Qwen, DeepSeek, GLM): character-based estimation
    - Fallback: generic character estimation
    """
    if not text:
        return 0

    model_lower = model_name.lower()

    # OpenAI models → tiktoken
    if any(kw in model_lower for kw in ("gpt", "o1", "o3", "chatgpt")):
        return _count_with_tiktoken(text, "cl100k_base")

    # Claude models → tiktoken (same tokenizer)
    if "claude" in model_lower:
        return _count_with_tiktoken(text, "cl100k_base")

    # Chinese-first models → character-based heuristic
    if any(kw in model_lower for kw in ("qwen", "deepseek", "glm", "ernie", "yi-", "moonshot")):
        return _estimate_chinese_tokens(text)

    # Default: character-based estimation
    return _estimate_chinese_tokens(text)


def _count_with_tiktoken(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count tokens using tiktoken."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding(encoding_name)
        return len(enc.encode(text))
    except Exception:
        # Fallback if tiktoken is not available
        return _estimate_chinese_tokens(text)


def _estimate_chinese_tokens(text: str) -> int:
    """
    Estimate tokens for Chinese-heavy text.
    - Chinese characters: ~1.5 characters per token
    - English words: ~1.3 tokens per word
    - Mixed text uses a blend
    """
    # Count Chinese characters
    chinese_chars = len(re.findall(r"[一-鿿]", text))
    # Count non-Chinese characters
    non_chinese_len = len(text) - chinese_chars

    # Rough estimation
    chinese_tokens = int(chinese_chars / 1.5)
    non_chinese_tokens = int(non_chinese_len / 4)  # ~4 chars per token for English

    return max(1, chinese_tokens + non_chinese_tokens)
