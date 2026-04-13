"""Planner interfaces, parsing helpers, and client implementations."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib import error, request

from icu_qa.config import Settings
from icu_qa.data.schema import DatasetSchema
from icu_qa.planning.prompt_templates import (
    build_planner_system_prompt,
    build_planner_user_prompt,
)
from icu_qa.planning.validator import ValidationResult, validate_plan_dict


class PlannerError(RuntimeError):
    """Base exception for planner failures."""


class PlannerParseError(PlannerError):
    """Raised when planner output cannot be parsed as JSON."""


class PlannerRejectedError(PlannerError):
    """Raised when planner output fails validation."""


class PlannerTransportError(PlannerError):
    """Raised when the remote planner transport fails."""


@dataclass(slots=True)
class PlannerRequest:
    """Structured input to the planning layer."""

    question: str
    schema: DatasetSchema
    few_shot_examples: list[dict[str, object]] = field(default_factory=list)


@dataclass(slots=True)
class PlannerResponse:
    """Structured output from the planning layer."""

    raw_text: str
    plan: dict[str, Any] | None = None
    validation: ValidationResult | None = None
    attempts: int = 1


class PlannerClient(Protocol):
    """Protocol for planner implementations."""

    def build_messages(self, request: PlannerRequest) -> list[dict[str, str]]:
        """Build planner messages for a request."""

    def plan(self, request: PlannerRequest) -> PlannerResponse:
        """Return a planner response for a request."""


class PlannerTransport(Protocol):
    """Protocol for remote or mocked message transports."""

    def complete(self, messages: list[dict[str, str]]) -> str:
        """Return the raw planner output text."""


@dataclass(slots=True)
class HTTPPlannerTransport:
    """HTTP transport for OpenAI-compatible chat completion endpoints."""

    api_url: str
    api_key: str
    model: str
    temperature: float = 0.0
    timeout_seconds: float = 60.0

    @classmethod
    def from_settings(cls, settings: Settings) -> "HTTPPlannerTransport":
        if not settings.planner_api_key:
            raise PlannerTransportError(
                "Missing planner API key. Set ICU_QA_PLANNER_API_KEY to enable live planning."
            )
        return cls(
            api_url=settings.planner_api_url,
            api_key=settings.planner_api_key,
            model=settings.planner_model_name,
            temperature=settings.planner_temperature,
            timeout_seconds=settings.planner_timeout_seconds,
        )

    def complete(self, messages: list[dict[str, str]]) -> str:
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
            "messages": messages,
        }
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            self.api_url,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                raw_payload = response.read().decode("utf-8")
        except error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise PlannerTransportError(
                f"Planner HTTP request failed with status {exc.code}: {error_body}"
            ) from exc
        except error.URLError as exc:
            raise PlannerTransportError(f"Planner network error: {exc.reason}") from exc

        try:
            decoded = json.loads(raw_payload)
        except json.JSONDecodeError as exc:
            raise PlannerTransportError("Planner transport returned non-JSON HTTP response.") from exc

        return self._extract_message_content(decoded)

    @staticmethod
    def _extract_message_content(decoded: dict[str, Any]) -> str:
        choices = decoded.get("choices")
        if not isinstance(choices, list) or not choices:
            raise PlannerTransportError("Planner HTTP response did not include choices.")

        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts = [
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("type") == "text"
            ]
            merged = "".join(text_parts).strip()
            if merged:
                return merged
        raise PlannerTransportError("Planner HTTP response did not include text content.")


def build_messages(request: PlannerRequest) -> list[dict[str, str]]:
    """Build planner messages for the given request."""

    return [
        {"role": "system", "content": build_planner_system_prompt()},
        {
            "role": "user",
            "content": build_planner_user_prompt(
                question=request.question,
                schema=request.schema,
                few_shot_examples=request.few_shot_examples,
            ),
        },
    ]


def build_repair_messages(
    request: PlannerRequest,
    previous_raw_text: str,
    error_message: str,
) -> list[dict[str, str]]:
    """Build a repair prompt sequence after parse or validation failure."""

    repair_instruction = (
        "Your previous response could not be accepted. "
        "Return corrected JSON only. "
        "Do not include markdown fences, explanation, or prose. "
        f"Error: {error_message}"
    )
    messages = build_messages(request)
    messages.append({"role": "assistant", "content": previous_raw_text})
    messages.append({"role": "user", "content": repair_instruction})
    return messages


def parse_planner_output(raw_text: str) -> dict[str, Any]:
    """Parse raw planner output into a JSON plan dictionary.

    Accepts plain JSON or JSON wrapped in markdown code fences.
    """

    candidate = raw_text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].startswith("```"):
            candidate = "\n".join(lines[1:-1]).strip()
            if candidate.lower().startswith("json\n"):
                candidate = candidate[5:].strip()

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise PlannerParseError(f"Planner output is not valid JSON: {exc}") from exc

    if not isinstance(parsed, dict):
        raise PlannerParseError("Planner output must decode to a JSON object.")
    return parsed


class StructuredPlanner:
    """Planner client that delegates text generation to a transport.

    This class is the main Phase 2 planner interface. It is transport-agnostic,
    which keeps prompt construction, parsing, and validation separated from the
    eventual remote model integration.
    """

    def __init__(
        self,
        transport: PlannerTransport,
        validate_output: bool = True,
        max_repair_attempts: int = 1,
    ) -> None:
        self.transport = transport
        self.validate_output = validate_output
        self.max_repair_attempts = max_repair_attempts

    def build_messages(self, request: PlannerRequest) -> list[dict[str, str]]:
        return build_messages(request)

    def plan(self, request: PlannerRequest) -> PlannerResponse:
        messages = self.build_messages(request)
        last_error: PlannerError | None = None

        for attempt in range(1, self.max_repair_attempts + 2):
            raw_text = self.transport.complete(messages)
            try:
                plan = parse_planner_output(raw_text)
                validation: ValidationResult | None = None
                if self.validate_output:
                    validation = validate_plan_dict(plan, request.schema)
                    if not validation.is_valid:
                        raise PlannerRejectedError("; ".join(validation.errors))

                return PlannerResponse(
                    raw_text=raw_text,
                    plan=plan,
                    validation=validation,
                    attempts=attempt,
                )
            except (PlannerParseError, PlannerRejectedError) as exc:
                last_error = exc
                if attempt > self.max_repair_attempts:
                    raise exc
                messages = build_repair_messages(request, raw_text, str(exc))

        if last_error is None:
            raise PlannerError("Planner failed without returning an explicit error.")
        raise last_error


class StaticJSONPlannerTransport:
    """Transport that always returns the same JSON payload.

    Useful for local testing, examples, and deterministic demos.
    """

    def __init__(self, raw_response: str) -> None:
        self.raw_response = raw_response

    def complete(self, messages: list[dict[str, str]]) -> str:
        _ = messages
        return self.raw_response


class SequentialPlannerTransport:
    """Transport that returns a sequence of responses across retries."""

    def __init__(self, responses: list[str]) -> None:
        if not responses:
            raise ValueError("SequentialPlannerTransport requires at least one response.")
        self.responses = responses
        self.call_count = 0

    def complete(self, messages: list[dict[str, str]]) -> str:
        _ = messages
        index = min(self.call_count, len(self.responses) - 1)
        self.call_count += 1
        return self.responses[index]


def build_default_planner(
    settings: Settings | None = None,
    *,
    validate_output: bool = True,
    max_repair_attempts: int = 1,
) -> StructuredPlanner:
    """Build the default live planner from environment-backed settings."""

    active_settings = settings or Settings()
    transport = HTTPPlannerTransport.from_settings(active_settings)
    return StructuredPlanner(
        transport=transport,
        validate_output=validate_output,
        max_repair_attempts=max_repair_attempts,
    )


class StubPlanner:
    """Backward-compatible deterministic stub planner.

    Phase 2 keeps this class as a convenience wrapper around StructuredPlanner
    so existing demos do not break while the remote client is being implemented.
    """

    def __init__(self) -> None:
        placeholder_plan = {
            "intent": "unsupported_stub",
            "analysis_type": "descriptive_summary",
            "select": [],
            "filters": [],
            "group_by": [],
            "aggregations": [],
            "comparisons": [],
            "order_by": [],
            "limit": None,
            "requires_clarification": True,
            "confidence": 0.0,
            "notes": ["TODO: integrate remote planner service."],
        }
        self._planner = StructuredPlanner(
            transport=StaticJSONPlannerTransport(json.dumps(placeholder_plan)),
            validate_output=True,
            max_repair_attempts=1,
        )

    def build_messages(self, request: PlannerRequest) -> list[dict[str, str]]:
        return self._planner.build_messages(request)

    def plan(self, request: PlannerRequest) -> PlannerResponse:
        return self._planner.plan(request)
