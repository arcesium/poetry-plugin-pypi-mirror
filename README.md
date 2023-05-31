# poetry-plugin-pypi-mirror

## Description

*poetry-plugin-pypi-mirror* is a
[plugin](https://python-poetry.org/docs/master/plugins/) for
[poetry](https://python-poetry.org/), the Python packaging and dependency
manager. It enables poetry to substitute connections to pypi.org with
connections to a pypi.org mirror or pull-through cache **without requiring
project configuration changes**. This is ideal for situations where an
access-restricted or otherwise unsuitable-for-general-use pypi.org mirror must
be used by a subset of project contributors. For example:

* A private PyPI mirror internal to a business, required by company policy
* A limited-access PyPI mirror in a region where pypi.org is restricted
* A regional mirror that is more performant for a few users, and less performant
  for everyone else

These mirrors can be used without this plugin by [adding them as project
repositories](https://python-poetry.org/docs/repositories/). However, this
requires the mirror to be included in the project's configuration, and this also
results in source entries for the mirror appearing in `poetry.lock`. Since only
a subset of project contributors can use these mirrors, that subset of users
would need to replace and remove references to the mirror repository each time
they want to contribute their changes back to the project. This is suboptimal.

## Usage

### Installation

Follow poetry's [plugin installation instructions](https://python-poetry.org/docs/master/plugins/#using-plugins), replacing `poetry-plugin` with `poetry-plugin-pypi-mirror`.

### Specifying a mirror

To specify a mirror, you can either define `plugins.pypi_mirror.url` in poetry's
[configuration](https://python-poetry.org/docs/configuration/), or set
environment variable `POETRY_PYPI_MIRROR_URL` to the full URL for a [PEP
503](https://peps.python.org/pep-0503/)-compatible mirror. When both are set the
environment variable will be used.

#### Poetry config example

```toml
[plugins]
[plugins.pypi_mirror]
url = "https://example.org/repository/pypi-proxy/simple/"
```

... in [either](https://python-poetry.org/docs/configuration/) a project's
`poetry.toml` (for per-project configuration), or the user's `config.toml`.

#### Environment variable example

```shell
POETRY_PYPI_MIRROR_URL=https://example.org/repository/pypi-proxy/simple/ poetry add pendulum
```
...or...

```shell
export POETRY_PYPI_MIRROR_URL=https://example.org/repository/pypi-proxy/simple/
poetry add cleo # uses mirror specified in first line
poetry lock     # also uses mirror specified in first line
```

## Compatibility

*poetry-plugin-pypi-mirror* depends on poetry internals which can change between
poetry releases. It's important to ensure compatibility between the poetry
version in use and the plugin version in use.

| Poetry version(s) | Compatible plugin version(s) |
|-------------------|------------------------------|
| >= 1.3, < 1.6     | ^0.3.1                       |
| ~1.2.1            | < 0.3.0                      |

## See also

* [python-poetry/poetry#1632](https://github.com/python-poetry/poetry/issues/1632) - poetry feature request to add support for global repository URL replacement
