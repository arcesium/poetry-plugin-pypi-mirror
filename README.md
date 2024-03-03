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

#### Authentication

If the mirror you're using requires authentication, you can add the credentials
like you would for any other repository.

Please note that repository names are case-sensitive, so it is important that
you configure the credentials for `PyPI`. `pypi` or other variations will not
work.

```shell
poetry config http-basic.PyPI <username> <password/token>
```

## Compatibility

*poetry-plugin-pypi-mirror* depends on poetry internals which can change between
poetry releases. It's important to ensure compatibility between the poetry
version in use and the plugin version in use.

| Poetry version(s) | Compatible plugin version(s) |
|-------------------|------------------------------|
| >= 1.3, < 1.9     | ^0.4.2                       |
| ~1.2.1            | < 0.3.0                      |

## Contributing

To contribute, open a [pull
request](https://github.com/arcesium/poetry-plugin-pypi-mirror/pulls).

### Sign your work

All commits must be signed to be accepted. Your signature certifies that you
have the right to submit your contribution(s) to the project, in accordance with
the principles described in the [Developer Certificate of
Origin](https://developercertificate.org/).

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

To sign your commits, use the template below to generate a signature, and then
add that signature to your commit message(s):

```
Signed-off-by: Your Name <Your.Name@example.com>
```

You must use your true name. Pseudonyms are not permitted.

If you have set `git`'s `user.name` and `user.email`, you can sign commits
easily at commit time using `git commit -s`.

## See also

* [python-poetry/poetry#1632](https://github.com/python-poetry/poetry/issues/1632) - poetry feature request to add support for global repository URL replacement
