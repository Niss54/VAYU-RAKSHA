import pytest

from shadowcast_archiver.config import Settings


def test_from_env_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("ARCHIVE_BUCKET", "ARCHIVE_MAX_ATTEMPTS"):
        monkeypatch.delenv(key, raising=False)

    settings = Settings.from_env()

    assert settings == Settings()
    assert settings.bucket == "argmax-cyclone-2026-archive"


def test_from_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARCHIVE_BUCKET", "shadowcast-archive")
    monkeypatch.setenv("ARCHIVE_MAX_ATTEMPTS", "5")
    monkeypatch.setenv("ARCHIVE_RETRY_BACKOFF_S", "0.5")

    settings = Settings.from_env()

    assert settings.bucket == "shadowcast-archive"
    assert settings.max_attempts == 5
    assert settings.retry_backoff_s == 0.5


def test_from_env_rejects_non_numeric(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARCHIVE_MAX_ATTEMPTS", "three")

    with pytest.raises(ValueError, match="three"):
        Settings.from_env()
