"""Token counting and context trimming for LLM context windows."""

import logging

import tiktoken

logger = logging.getLogger(__name__)

DEFAULT_MODEL_WINDOW = 128_000


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count tokens in text using tiktoken."""
    if not text:
        return 0
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def trim_context(
    prompt: str,
    context: str,
    max_fraction: float = 0.75,
    max_tokens: int = DEFAULT_MODEL_WINDOW,
) -> str:
    """Trim search context if combined tokens exceed budget.

    Keeps the prompt intact and truncates context lines from the
    end until the total fits within max_fraction of max_tokens.
    """
    budget = int(max_tokens * max_fraction)
    prompt_tokens = count_tokens(prompt)
    available = budget - prompt_tokens
    if available <= 0:
        logger.warning("Prompt alone exceeds token budget")
        return ""

    context_tokens = count_tokens(context)
    if context_tokens <= available:
        return context

    logger.info(
        "Trimming context from %d to ~%d tokens",
        context_tokens,
        available,
    )
    lines = context.split("\n")
    kept: list[str] = []
    running = 0
    for line in lines:
        line_tokens = count_tokens(line)
        if running + line_tokens > available:
            break
        kept.append(line)
        running += line_tokens

    return "\n".join(kept)
