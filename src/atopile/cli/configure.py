"""
Configure the user's system for atopile development.
"""

import logging

from atopile.telemetry import capture

logger = logging.getLogger(__name__)


@capture("cli:configure_start", "cli:configure_end")
def configure() -> None:
    """
    Configure the user's system for atopile development.
    """
    from textwrap import dedent

    from faebryk.libs.logging import rich_print_robust

    # Just here for legacy support
    rich_print_robust(
        dedent(
            """
            This command is deprecated and will be removed in a future version.
            Configuration/Setup should be automatically handled.
            """
        )
    )


def setup() -> None:
    # Cleanup legacy config file
    from faebryk.libs.paths import get_config_dir

    try:
        _LEGACY_CFG_PATH = get_config_dir() / "configured_for.yaml"
        if _LEGACY_CFG_PATH.exists():
            _LEGACY_CFG_PATH.unlink()
    except Exception as e:
        logger.warning(f"Couldn't remove legacy config file: {e!r}")

    # if running is ci skip plugin installation
    from atopile.telemetry import PropertyLoaders

    if PropertyLoaders.ci_provider():
        return
    
    # KiCad plugin setup - wrap everything in try-except to prevent any blocking
    # If anything hangs or fails, we just skip it and continue
    # Note: We can't use threading timeout in Python, so we rely on try-except
    # to catch any exceptions and make imports lazy to avoid blocking
    try:
        # Call install_kicad_plugin directly (it's defined in this module)
        install_kicad_plugin()
    except Exception as e:
        logger.debug(f"Couldn't install plugin (non-fatal): {e!r}", exc_info=e)

    try:
        # Import only when needed to avoid blocking on import
        from faebryk.libs.kicad.ipc import enable_plugin_api
        enable_plugin_api()
    except Exception as e:
        logger.debug(f"Couldn't enable plugin api (non-fatal): {e!r}", exc_info=e)


def install_kicad_plugin() -> None:
    """Install the kicad plugin."""
    # TODO switch to new plugin as soon as group serialize ipc works in kicad
    # TODO then also remove legacy plugin from existing installations
    from atopile.kicad_plugin.lib import install_kicad_legacy_plugin

    install_kicad_legacy_plugin()
