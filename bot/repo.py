"""The bot's own clone of the site, and the pushes it makes to it.

Everything that touches git goes through `Repo`, which holds a lock so two
people uploading at the same time queue up instead of colliding on push.
"""

import asyncio
import logging
import os
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)


class GitError(RuntimeError):
    pass


class Repo:
    def __init__(self, *, url: str, token: str, branch: str, workdir: Path):
        self._url = url
        self._token = token
        self.branch = branch
        self.path = workdir
        self.lock = asyncio.Lock()

    # -- plumbing ---------------------------------------------------------

    @property
    def _authed_url(self) -> str:
        return self._url.replace("https://", f"https://x-access-token:{self._token}@")

    def _git(self, *args: str, check: bool = True) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.path,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if check and result.returncode != 0:
            # Never let the token reach a log line or a Telegram message.
            stderr = result.stderr.replace(self._token, "***")
            raise GitError(f"git {args[0]} failed: {stderr.strip()}")
        return result.stdout.strip()

    def _redact(self, text: str) -> str:
        return text.replace(self._token, "***")

    # -- lifecycle --------------------------------------------------------

    def clone(self) -> None:
        """Fresh clone at startup, so a half-finished state never persists."""
        if self.path.exists():
            shutil.rmtree(self.path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["git", "clone", "--depth", "50", "--branch", self.branch,
             self._authed_url, str(self.path)],
            capture_output=True, text=True, timeout=600,
        )
        if result.returncode != 0:
            raise GitError(f"clone failed: {self._redact(result.stderr).strip()}")
        self._git("config", "user.name", os.environ.get("GIT_AUTHOR_NAME", "Mayuri'z bot"))
        self._git("config", "user.email",
                  os.environ.get("GIT_AUTHOR_EMAIL", "bot@users.noreply.github.com"))
        log.info("cloned %s (%s) into %s", self._url, self.branch, self.path)

    def refresh(self) -> None:
        """Catch up with anything pushed since the last upload."""
        self._git("fetch", "origin", self.branch)
        self._git("reset", "--hard", f"origin/{self.branch}")
        self._git("clean", "-fd")

    def discard(self) -> None:
        """Throw away a failed half-edit so the next upload starts clean."""
        try:
            self._git("reset", "--hard", check=False)
            self._git("clean", "-fd", check=False)
        except Exception:
            log.exception("could not discard working changes")

    # -- writing ----------------------------------------------------------

    def commit_and_push(self, message: str) -> str:
        """Commit everything staged in the working tree and push. Returns the sha."""
        self._git("add", "-A")
        if not self._git("status", "--porcelain"):
            raise GitError("nothing changed — no commit made")
        self._git("commit", "-m", message)
        sha = self._git("rev-parse", "--short", "HEAD")

        for attempt in range(3):
            result = subprocess.run(
                ["git", "push", "origin", self.branch],
                cwd=self.path, capture_output=True, text=True, timeout=300,
            )
            if result.returncode == 0:
                return sha
            # Somebody else pushed in between: replay this commit on top and retry.
            log.warning("push rejected (attempt %d), rebasing", attempt + 1)
            rebase = subprocess.run(
                ["git", "pull", "--rebase", "origin", self.branch],
                cwd=self.path, capture_output=True, text=True, timeout=300,
            )
            if rebase.returncode != 0:
                self._git("rebase", "--abort", check=False)
                raise GitError(
                    "couldn't merge with what's already on GitHub — "
                    f"needs a human: {self._redact(rebase.stderr).strip()}"
                )
            sha = self._git("rev-parse", "--short", "HEAD")
        raise GitError("push kept being rejected — give it a minute and try again")

    def revert_last_bot_commit(self) -> tuple[str, str]:
        """Undo the most recent commit. Returns (reverted subject, new sha)."""
        subject = self._git("log", "-1", "--pretty=%s")
        self._git("revert", "--no-edit", "HEAD")
        sha = self._git("rev-parse", "--short", "HEAD")
        result = subprocess.run(
            ["git", "push", "origin", self.branch],
            cwd=self.path, capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            raise GitError(f"couldn't push the undo: {self._redact(result.stderr).strip()}")
        return subject, sha

    def last_commits(self, n: int = 5) -> list[str]:
        return self._git("log", f"-{n}", "--pretty=%h  %s").splitlines()
