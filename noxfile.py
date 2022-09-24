"""Nox Sessions."""
import os
import tempfile
from typing import Any

import nox
from nox.sessions import Session


package = "modern_python_template"
nox.options.sessions = "lint", "safety", "mypy", "pytype", "tests"
locations = "src", "tests", "noxfile.py"


def install_with_constraints(session: Session, *args: str, **kwargs: Any) -> None:
    """Install packages constrained by Poetry's lock file.

    This function is a wrapper for nox.sessions.Session.install. It
    invokes pip to install packages inside of the session's virtualenv.
    Additionally, pip is passed a constraints file generated from
    Poetry's lock file, to ensure that the packages are pinned to the
    versions specified in poetry.lock. This allows you to manage the
    packages as Poetry development dependencies.

    Arguments:
        session: The Session object.
        args: Command-line arguments for pip.
        kwargs: Additional keyword arguments for Session.install.

    """
    with tempfile.NamedTemporaryFile(dir=os.getcwd(), delete=False) as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)
    os.remove(requirements.name)


@nox.session(python=["3.8", "3.7"])
def tests(session: Session) -> None:
    """Run the tests suite.

    Args:
        session (Session): Nox Session
    """
    args = session.posargs or ["--cov", "-m", "not e2e"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock", "--use-deprecated=legacy-resolver"
    )
    session.run("pytest", *args)


@nox.session(python=["3.8", "3.7"])
def black(session: Session) -> None:
    """Run black code formatter.

    Args:
        session (Session): Nox Session
    """
    args = session.posargs or locations
    install_with_constraints(session, "black", "--use-deprecated=legacy-resolver")
    session.run("black", *args)


@nox.session(python=["3.8", "3.7"])
def lint(session: Session) -> None:
    """Lint using Flake8. Configurations in .flake8.

    Args:
        session (Session): Nox Session
    """
    args = session.posargs or locations
    install_with_constraints(
        session,
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
        "darglint",
        "--use-deprecated=legacy-resolver",
    )
    session.run("flake8", *args)


@nox.session(python="3.8")
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages.

    Args:
        session (Session): Nox Session
    """
    with tempfile.NamedTemporaryFile(dir=os.getcwd(), delete=False) as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        install_with_constraints(session, "safety", "--use-deprecated=legacy-resolver")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")


@nox.session(python=["3.8", "3.7"])
def mypy(session: Session) -> None:
    """Static Type checking using mypy.

    Args:
        session (Session): Nox Session
    """
    args = session.posargs or locations
    install_with_constraints(session, "mypy", "--use-deprecated=legacy-resolver")
    session.run("mypy", *args)


@nox.session(python="3.7")
def pytype(session: Session) -> None:
    """Run the static type checker using pytype.

    Args:
        session (Session): Nox Session
    """
    args = session.posargs or ["--disable=import-error", *locations]
    install_with_constraints(session, "pytype", "--use-deprecated=legacy-resolver")
    session.run("pytype", *args)


@nox.session(python=["3.8", "3.7"])
def typeguard(session: Session) -> None:
    """Runtime type checking using typegaurd.

    Args:
        session (Session): Nox Session
    """
    args = session.posargs or ["-m", "not e2e"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session,
        "pytest",
        "pytest-mock",
        "typeguard",
        "--use-deprecated=legacy-resolver",
    )
    session.run("pytest", f"--typeguard-packages={package}", *args)


@nox.session(python=["3.8", "3.7"])
def xdoctest(session: Session) -> None:
    """Run examples with xdoctest."""
    args = session.posargs or ["all"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(session, "xdoctest", "--use-deprecated=legacy-resolver")
    session.run("python", "-m", "xdoctest", package, *args)
