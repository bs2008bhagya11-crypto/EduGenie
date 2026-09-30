import time
from functools import lru_cache
from typing import TypeVar, Type

from fastapi import HTTPException
from google import genai
from google.genai import types

from config import settings

T = TypeVar("T")

MAX_RETRIES = 2

RETRYABLE_ERRORS = (
    "429",
    "500",
    "502",
    "503",
    "504",
    "RESOURCE_EXHAUSTED",
    "UNAVAILABLE",
    "INTERNAL",
    "DEADLINE_EXCEEDED",
)


@lru_cache
def get_client() -> genai.Client:
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured.",
        )

    return genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(
            timeout=settings.request_timeout_seconds * 1000
        ),
    )


def is_retryable_error(exc: Exception) -> bool:
    text = str(exc).upper()
    return any(code in text for code in RETRYABLE_ERRORS)


def call_model(
    client: genai.Client,
    model: str,
    prompt: str,
    *,
    system_instruction: str | None = None,
    temperature: float = 0.35,
    max_output_tokens: int = 1600,
) -> str:

    last_error = None

    for attempt in range(MAX_RETRIES + 1):

        try:
            print(
                f"Calling Gemini model: {model} "
                f"(attempt {attempt + 1})"
            )

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                ),
            )

            result = (response.text or "").strip()

            if not result:
                raise ValueError(
                    f"{model} returned empty response."
                )

            return result

        except Exception as exc:

            last_error = exc

            print(
                f"Model {model} error: {exc}"
            )

            if (
                is_retryable_error(exc)
                and attempt < MAX_RETRIES
            ):
                delay = 2 ** (attempt + 1)

                print(
                    f"Retrying {model} "
                    f"in {delay} seconds..."
                )

                time.sleep(delay)

            else:
                break

    raise last_error


def generate_text(
    prompt: str,
    *,
    system_instruction: str | None = None,
    temperature: float = 0.35,
    max_output_tokens: int = 1600,
) -> str:

    client = get_client()

    primary = settings.gemini_model
    fallback = settings.gemini_fallback_model

    print("=" * 60)
    print(f"PRIMARY MODEL: {primary}")
    print(f"FALLBACK MODEL: {fallback}")
    print("=" * 60)

    # Primary model
    try:
        return call_model(
            client,
            primary,
            prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

    except Exception as primary_error:

        print("=" * 60)
        print(f"PRIMARY FAILED: {primary}")
        print(primary_error)
        print("=" * 60)

    # Fallback model
    if fallback and fallback != primary:

        try:

            print("=" * 60)
            print(f"SWITCHING TO FALLBACK: {fallback}")
            print("=" * 60)

            return call_model(
                client,
                fallback,
                prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )

        except Exception as fallback_error:

            print("=" * 60)
            print(f"FALLBACK FAILED: {fallback}")
            print(fallback_error)
            print("=" * 60)

            raise HTTPException(
                status_code=502,
                detail=(
                    f"Primary model {primary} and "
                    f"fallback model {fallback} failed."
                ),
            ) from fallback_error

    raise HTTPException(
        status_code=502,
        detail=f"Gemini model {primary} failed.",
    )


def generate_structured(
    prompt: str,
    response_schema: Type[T],
    *,
    system_instruction: str | None = None,
    temperature: float = 0.25,
    max_output_tokens: int = 2400,
) -> T:

    client = get_client()

    models = [
        settings.gemini_model,
        settings.gemini_fallback_model,
    ]

    last_error = None

    for model in models:

        if not model:
            continue

        try:

            print(f"STRUCTURED MODEL: {model}")

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                ),
            )

            parsed = getattr(
                response,
                "parsed",
                None,
            )

            if parsed is not None:
                return parsed

        except Exception as exc:

            last_error = exc

            print(
                f"Structured model {model} failed: {exc}"
            )

            continue

    raise HTTPException(
        status_code=502,
        detail=(
            f"All Gemini models failed. "
            f"Last error: {last_error}"
        ),
    ) from last_error