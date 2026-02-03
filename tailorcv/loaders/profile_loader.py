"""Profile loader for profile.yaml inputs."""

from pathlib import Path

import yaml

from tailorcv.schema.profile_schema import Profile


class ProfileLoadError(Exception):
    """Raised when profile.yaml cannot be loaded or validated."""

    pass


def load_profile(profile_path: str | Path) -> Profile:
    """
    Load and validate a profile.yaml file.

    :param profile_path: Path to the profile.yaml file.
    :type profile_path: str | pathlib.Path
    :return: Validated profile object.
    :rtype: tailorcv.schema.profile_schema.Profile
    :raises ProfileLoadError: If the file cannot be read or fails validation.
    """
    profile_path = Path(profile_path)

    if not profile_path.exists():
        raise ProfileLoadError(f"Profile file not found: {profile_path}")

    try:
        with profile_path.open("r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
    except Exception as e:
        raise ProfileLoadError(f"Failed to read YAML file: {e}")

    try:
        profile = Profile.model_validate(raw_data)
    except Exception as e:
        raise ProfileLoadError(f"Profile schema validation failed: {e}")

    return profile
