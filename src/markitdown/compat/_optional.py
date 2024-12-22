from typing import Literal
import sys
import importlib
import types
import warnings

INSTALL_MAPPING = {}

VERSIONS = {}


def get_version(module: types.ModuleType) -> str:
    version = getattr(module, "__version__", None)

    if version is None:
        raise ValueError("Can't determine version for {module.__name__}")
    return version


def import_optional(
    name: str,
    extra: str = "",
    min_version: str | None = None,
    *,
    errors: Literal["raise", "warn", "ignore"] = "raise",
):
    """Import an optional dependency."""
    assert errors in {"raise", "warn", "ignore"}

    package_name = INSTALL_MAPPING.get(name)
    install_name = package_name if package_name is not None else name

    msg = (
        f"Missing optional dependency '{install_name}'. {extra} "
        f"Use pip to install {install_name}."
    )

    try:
        module = importlib.import_module(name)
    except ImportError as e:
        if errors == "raise":
            raise ImportError(msg) from e
        return None

    # Handle submodules
    parent = name.split(".")[0]
    if parent != name:
        install_name = parent
        module_to_get = sys.modules[install_name]
    else:
        module_to_get = module
    minimum_version = min_version if min_version is not None else VERSIONS.get(parent)
    if min_version:
        version = get_version(module_to_get)
        if version and version < minimum_version:
            msg = (
                f"Need at least version {min_version} of '{install_name}' "
                f"(found {version}). {extra}"
            )
            if errors == "warn":
                warnings.warn(msg, UserWarning)
                return None
            elif errors == "raise":
                raise ImportError(msg)
            return None
    return module
