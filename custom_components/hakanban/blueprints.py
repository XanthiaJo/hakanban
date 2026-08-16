"""On-demand blueprint management for native HA automations."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from homeassistant.core import HomeAssistant

DOMAIN: Final = "hakanban"
BLUEPRINT_DIR: Final = "automation"


def _source_dir() -> Path:
    """Directory inside the package that holds the blueprint files."""
    return Path(__file__).parent / "blueprints" / BLUEPRINT_DIR


def _target_dir(hass: HomeAssistant) -> Path:
    return Path(hass.config.path("blueprints")) / BLUEPRINT_DIR / DOMAIN


def list_blueprints() -> list[dict]:
    """Return metadata for every built-in blueprint."""
    source = _source_dir()
    if not source.is_dir():
        return []
    out = []
    for f in sorted(source.glob("*.yaml")):
        out.append({"filename": f.name, "name": f.stem})
    return out


def installed_blueprints(hass: HomeAssistant) -> list[str]:
    """Return filenames of blueprints currently installed in the user's config."""
    target = _target_dir(hass)
    if not target.is_dir():
        return []
    return sorted(f.name for f in target.glob("*.yaml"))


def install_blueprint(hass: HomeAssistant, filename: str) -> None:
    """Copy a built-in blueprint into the user's config/blueprints tree."""
    source = _source_dir() / filename
    if not source.is_file():
        raise ValueError(f"Unknown blueprint: {filename}")

    target = _target_dir(hass)
    target.mkdir(parents=True, exist_ok=True)
    (target / filename).write_text(
        source.read_text(encoding="utf-8"), encoding="utf-8"
    )


def uninstall_blueprint(hass: HomeAssistant, filename: str) -> None:
    """Remove a blueprint from the user's config/blueprints tree."""
    target = _target_dir(hass) / filename
    if target.is_file():
        target.unlink()


def blueprint_status(hass: HomeAssistant) -> list[dict]:
    """Return all built-in blueprints with their installed state."""
    installed = set(installed_blueprints(hass))
    return [
        {**bp, "installed": bp["filename"] in installed}
        for bp in list_blueprints()
    ]
