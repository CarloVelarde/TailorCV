"""Default RenderCV design/locale/settings blocks (one-page bias)."""

from __future__ import annotations

from typing import Any, Dict


def get_default_design() -> Dict[str, Any]:
    """
    Return the default RenderCV design block.

    The defaults aim for a one-page resume. Users can override these settings.
    This block stays intentionally minimal to reduce schema errors while still
    nudging the output toward a single page.

    :return: Default design block.
    :rtype: dict[str, typing.Any]
    """
    return {
        "theme": "engineeringresumes",
        "page": {
            "size": "us-letter",
            "top_margin": "0.7in",
            "bottom_margin": "0.7in",
            "left_margin": "0.7in",
            "right_margin": "0.7in",
            "show_footer": False,
        },
        "typography": {
            "line_spacing": "0.6em",
            "font_size": {"body": "10pt", "name": "24pt"},
        },
        "entries": {
            "date_and_location_width": "4.0cm",
        },
    }


def get_default_locale() -> Dict[str, Any]:
    """
    Return the default RenderCV locale block.

    This is intentionally minimal (language only) because RenderCV defaults
    to English and we want to avoid premature locale assumptions. Expansion
    points include date formats, translated section labels, and numeric formats.

    :return: Default locale block.
    :rtype: dict[str, typing.Any]
    """
    return {"language": "english"}


def get_default_settings() -> Dict[str, Any]:
    """
    Return the default RenderCV settings block.

    The empty dict defers to RenderCV defaults. This avoids accidental coupling
    to settings like `current_date` or output paths until the CLI is in place.

    :return: Default settings block.
    :rtype: dict[str, typing.Any]
    """
    return {}
