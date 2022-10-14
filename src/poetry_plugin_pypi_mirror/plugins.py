from __future__ import annotations

import os

from cleo.io.io import IO
from poetry.core.packages.package import Package
from poetry.core.semver.version import Version
from poetry.plugins.plugin import Plugin
from poetry.poetry import Poetry
from poetry.repositories.legacy_repository import LegacyRepository
from poetry.repositories.pypi_repository import PyPiRepository

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
        pypi_mirror_url = os.environ.get("POETRY_PYPI_MIRROR_URL")

        if not pypi_mirror_url:
            return

        for idx, repo in enumerate(poetry.pool.repositories):
            if repo.name == DEFAULT_REPO_NAME and isinstance(repo, PyPiRepository):
                # We preserve the ordering of poetry.pool.repositories to
                # maintain repository precedence
                poetry.pool.repositories[idx] = SourceStrippedLegacyRepository(
                    DEFAULT_REPO_NAME,
                    pypi_mirror_url,
                    config=poetry.config,
                    disable_cache=repo._disable_cache,
                )


class SourceStrippedLegacyRepository(LegacyRepository):
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
