import tempfile
import unittest
from pathlib import Path

from backend.app.core.config import SettingsError, load_settings


class SettingsTests(unittest.TestCase):
    def test_missing_api_key_raises_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "OPENAI_MODEL=gpt-4o-mini\nAPP_ENV=test\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SettingsError, "OPENAI_API_KEY"):
                load_settings(env_file=env_file, environ={})

    def test_secret_is_masked_and_file_values_are_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "OPENAI_API_KEY=test-secret-value\n"
                "OPENAI_MODEL=gpt-4o-mini\n"
                "APP_ENV=test\n",
                encoding="utf-8",
            )

            settings = load_settings(env_file=env_file, environ={})

            self.assertEqual(settings.openai_model, "gpt-4o-mini")
            self.assertEqual(settings.app_env, "test")
            self.assertEqual(
                settings.openai_api_key.get_secret_value(),
                "test-secret-value",
            )
            self.assertNotIn("test-secret-value", repr(settings))

    def test_environment_values_override_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "OPENAI_API_KEY=file-key\n"
                "OPENAI_MODEL=file-model\n"
                "APP_ENV=file\n",
                encoding="utf-8",
            )

            settings = load_settings(
                env_file=env_file,
                environ={
                    "OPENAI_API_KEY": "environment-key",
                    "OPENAI_MODEL": "environment-model",
                    "APP_ENV": "environment",
                },
            )

            self.assertEqual(settings.openai_model, "environment-model")
            self.assertEqual(settings.app_env, "environment")
            self.assertEqual(
                settings.openai_api_key.get_secret_value(),
                "environment-key",
            )


if __name__ == "__main__":
    unittest.main()
