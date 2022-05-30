import semver

from fl_suite import __version__


def test_version() -> None:
    """Tests that project version is SemVer."""
    semver.VersionInfo.parse(__version__)
