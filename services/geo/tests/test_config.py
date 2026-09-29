import pytest

from shadowcast_geo.config import SCENARIOS, Settings


def test_from_env_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("GEO_BUCKET", "GEO_ALLOWED_ORIGINS", "GEO_MAX_ATTEMPTS"):
        monkeypatch.delenv(key, raising=False)

    assert Settings.from_env() == Settings()


def test_from_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEO_BUCKET", "scenarios-bucket")
    monkeypatch.setenv("GEO_ALLOWED_ORIGINS", "https://shadowcast.vercel.app, http://localhost:3000")
    monkeypatch.setenv("GEO_MAX_ATTEMPTS", "4")

    settings = Settings.from_env()

    assert settings.bucket == "scenarios-bucket"
    assert settings.allowed_origins == ("https://shadowcast.vercel.app", "http://localhost:3000")
    assert settings.max_attempts == 4


def test_from_env_rejects_bad_number(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEO_HTTP_TIMEOUT_S", "soon")

    with pytest.raises(ValueError, match="soon"):
        Settings.from_env()


def test_exactly_one_reference_scenario() -> None:
    assert [s.id for s in SCENARIOS.values() if s.reference] == ["fani-2019"]
    assert all(s.truth_pre[1] <= s.truth_post[0] for s in SCENARIOS.values())
