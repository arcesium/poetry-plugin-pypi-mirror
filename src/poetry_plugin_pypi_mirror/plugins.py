from __future__ import annotations

import os

from cleo.io.io import IO
from poetry.config.config import Config
from poetry.core.constraints.version import Version
from poetry.core.packages.package import Package
from poetry.plugins.plugin import Plugin
from poetry.poetry import Poetry
from poetry.repositories.legacy_repository import LegacyRepository
from poetry.repositories.pypi_repository import PyPiRepository
from poetry.repositories.repository_pool import Priority

# Hopefully the default repo name never changes. It'd be nice if this value was
# exposed in poetry as a constant.
DEFAULT_REPO_NAME = "PyPI"


class PyPIMirrorPlugin(Plugin):
    # If pypi.org and common mirroring/pull-through-cache software used the same
    # standard API this plugin could simply modify the URL used by
    # PyPiRepository. Unfortunately, PyPiRepository uses the unstable
    # non-standard warehouse JSON API. To ensure maximum mirror compatibility
    # through standards compliance we replace the pypi.org PyPiRepository with a
    # (modified) LegacyRepository - which uses the PEP 503 API.
    def activate(self, poetry: Poetry, io: IO):
        # Environment var overrides poetry configuration
        pypi_mirror_url = os.environ.get("POETRY_PYPI_MIRROR_URL")
        pypi_mirror_url = pypi_mirror_url or poetry.config.get("plugins", {}).get(
            "pypi_mirror", {}
        ).get("url")

        if not pypi_mirror_url:
            return

        # If the PyPI Mirror requires authentication, the dependency resolving
        # process is handled by the Repository class we create. However,
        # dependency installation is performed by the Installer class, which
        # creates its own Authenticator.
        #
        # Because the Authenticator uses poetry's configuration to determine the
        # authentication settings for each repository, we must modify poetry's
        # config to include the PyPI mirror's URL. The Authenticator then will
        # use Keyring to read the credentials for that repository/URL as it
        # would with any other.
        poetry.config.merge(
            {"repositories": {DEFAULT_REPO_NAME: {"url": pypi_mirror_url}}}
        )

        # All keys are lowercased in public functions
        repo_key = DEFAULT_REPO_NAME.lower()

        pypi_prioritized_repository = poetry.pool._repositories.get(repo_key)

        if pypi_prioritized_repository is None or not isinstance(
            pypi_prioritized_repository.repository, PyPiRepository
        ):
            return

        replacement_repository = SourceStrippedLegacyRepository(
            DEFAULT_REPO_NAME,
            pypi_mirror_url,
            config=poetry.config,
            disable_cache=pypi_prioritized_repository.repository._disable_cache,
        )

        priority = pypi_prioritized_repository.priority

        poetry.pool.remove_repository(DEFAULT_REPO_NAME)
        poetry.pool.add_repository(
            repository=replacement_repository,
            default=priority == Priority.DEFAULT,
            secondary=priority == Priority.SECONDARY,
        )


class SourceStrippedLegacyRepository(LegacyRepository):
    def __init__(
        self,
        name: str,
        url: str,
        config: Config | None = None,
        disable_cache: bool = False,
    ) -> None:
        super().__init__(name, url, config, disable_cache)

    # Packages sourced from PyPiRepository repositories *do not* include their
    # source data in poetry.lock. This is unique to PyPiRepository. Packages
    # sourced from LegacyRepository repositories *do* include their source data
    # (type, url, reference) in poetry.lock. This becomes undesirable when we
    # replace the PyPiRepository with a LegacyRepository PyPI mirror, as the
    # LegacyRepository begins to write source data into the project. We want to
    # support mirror use without referencing the mirror repository within the
    # project, so this behavior is undesired.
    #
    # To work around this, we extend LegacyRepository. The extended version
    # drops source URL information from packages attributed to the repository,
    # preventing that source information from being included in the lockfile.
    def package(
        self, name: str, version: Version, extras: list[str] | None = None
    ) -> Package:
        try:
            index = self._packages.index(Package(name, version))
            package = self._packages[index]
        except ValueError:
            package = super().package(name, version, extras)
        # It is a bit uncomfortable for this plugin to be modifying an internal
        # attribute of the package object. That said, the parent class does the
        # same thing (although it's not released independently like this plugin
        # is). It'd be preferable if there was a way to convey our goal
        # explicitly to poetry so we could avoid unintentional breaking changes.
        #
        # As one example of the potential danger, the existence of a non-None
        # package._source_url value currently determines if source data will be
        # written to poetry.lock. If this conditional changes, users of the
        # plugin may suddenly see unexpected source entries in their lockfiles.
        package._source_url = None
        return package
