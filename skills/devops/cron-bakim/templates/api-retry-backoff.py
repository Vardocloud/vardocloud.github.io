"""
Reusable API call retry with exponential backoff for Hermes cron scripts.

Usage: copy this function into any script that makes OpenAI-compatible API calls.
Handles 429 rate limits with progressive backoff. Non-rate-limit errors are
re-raised immediately.

Dependencies: openai (pip install openai)
"""
from openai import OpenAI
import time


def call_with_retry(
    client: OpenAI,
    model: str,
    messages: list,
    system_prompt: str = None,
    max_tokens: int = 16384,
    temperature: float = 0.7,
    retries: int = 5,
    base_delay: int = 30,
    max_delay: int = 600,
) -> str:
    """
    Call OpenAI-compatible API with exponential backoff on 429.

    Args:
        client: OpenAI client instance.
        model: Model name (e.g. 'deepseek-v4-flash-free').
        messages: List of message dicts.
        system_prompt: Optional system message prepended to messages.
        max_tokens: Max completion tokens.
        temperature: Sampling temperature.
        retries: Max retry attempts on 429.
        base_delay: Initial backoff in seconds (doubles each attempt).
        max_delay: Max backoff in seconds.

    Returns:
        Response content string.

    Raises:
        Exception: Re-raises non-429 errors immediately.
        RuntimeError: If all retries exhausted.
    """
    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            error_str = str(e)
            if "429" in error_str or "rate_limit" in error_str.lower():
                if attempt < retries:
                    wait = min(base_delay * (2 ** attempt), max_delay)
                    print(f"  Rate limit hit (attempt {attempt}/{retries}), waiting {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"  Rate limit exhausted after {retries} attempts.")
            else:
                # Non-rate-limit error: re-raise immediately
                raise
    raise last_error


# Example usage:
if __name__ == "__main__":
    client = OpenAI(
        api_key="your-api-key",
        base_url="https://opencode.ai/zen/v1",
    )
    result = call_with_retry(
        client=client,
        model="deepseek-v4-flash-free",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(result)
