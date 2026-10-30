"""Environment-backed application settings with secret-safe representation."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

from pydantic import BaseModel, ConfigDict, SecretStr


class SettingsError(RuntimeError):
    """Raised when required application settings are missing or invalid."""


class Settings(BaseModel):
    """Validated settings shared by the backend and integration adapters."""

    model_config = ConfigDict(frozen=True)

    openai_api_key: SecretStr
    openai_model: str = "gpt-4o-mini"
    app_env: str = "development"


def _read_env_file(path: Path) -> dict[str, str]:
    """Read a small dotenv-compatible file without mutating process state."""

    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").strip()
        if "=" not in line:
            raise SettingsError(
                f"Invalid environment entry at {path}:{line_number}",
            )

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value

    return values


def load_settings(
    *,
    env_file: Path | str = Path(".env"),
    environ: Mapping[str, str] | None = None,
) -> Settings:
    """Load settings, preferring process environment over the local env file."""

    source_environment = os.environ if environ is None else environ
    file_values = _read_env_file(Path(env_file))

    def get_value(name: str, default: str = "") -> str:
        return source_environment.get(name, file_values.get(name, default)).strip()

    api_key = get_value("OPENAI_API_KEY")
    if not api_key:
        raise SettingsError(
            "OPENAI_API_KEY is required; set it in the server environment or .env",
        )

    model = get_value("OPENAI_MODEL", "gpt-4o-mini")
    if not model:
        raise SettingsError("OPENAI_MODEL must not be empty")

    app_env = get_value("APP_ENV", "development")
    if not app_env:
        raise SettingsError("APP_ENV must not be empty")

    return Settings(
        openai_api_key=SecretStr(api_key),
        openai_model=model,
        app_env=app_env,
    )
