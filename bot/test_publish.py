"""End-to-end test of an upload, against a throwaway git remote.

Exercises everything an upload does except talking to Telegram: clone,
resize, edit both product lists, commit, push, and undo.

    cd bot && python test_publish.py
"""

import io
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

from media import save_photo, slugify, unique_slug
from repo import Repo
from site_edit import insert_into_film, insert_into_index

REPO = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def check(condition: bool, message: str) -> None:
    print(f"  {'ok  ' if condition else 'FAIL'} {message}")
    if not condition:
        FAILURES.append(message)


def fake_photo(width: int = 2400, height: int = 3200) -> bytes:
    image = Image.new("RGB", (width, height), (200, 90, 74))
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=95)
    return buffer.getvalue()


def main() -> int:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        origin = tmp / "origin.git"

        # A bare clone of the real repo stands in for GitHub.
        subprocess.run(["git", "clone", "--bare", "--no-local", str(REPO), str(origin)],
                       check=True, capture_output=True)
        branch = subprocess.run(["git", "-C", str(REPO), "branch", "--show-current"],
                                check=True, capture_output=True, text=True).stdout.strip()

        repo = Repo(url=f"file://{origin}", token="unused", branch=branch,
                    workdir=tmp / "work")
        repo.clone()
        check((repo.path / "index.html").exists(), "clone brings down the site")

        before_images = len(list((repo.path / "images").glob("*.jpg")))

        # --- an upload ---
        raw = fake_photo()
        slug = unique_slug(slugify("Peacock Blue Test Bow"), repo.path / "images")
        check(slug == "peacock-blue-test-bow", "name becomes a sensible file slug")

        filename = save_photo(raw, repo.path / "images", slug)
        saved = Image.open(repo.path / "images" / filename)
        check(saved.width == 1100, f"photo is resized to 1100px wide (got {saved.width})")
        check(saved.height == 1467, f"aspect ratio is kept (got {saved.height})")

        insert_into_index(repo.path / "index.html", product_id=slug,
                          name="Peacock Blue Test Bow", cat="bows",
                          desc="A test piece.", image=filename)
        insert_into_film(repo.path / "video/src/theme.ts",
                         name="Peacock Blue Test Bow", cat="bows", image=filename)

        sha = repo.commit_and_push("Add Peacock Blue Test Bow to the shop")
        check(bool(sha), f"commit pushed ({sha})")

        # --- did it actually land on the "remote"? ---
        pushed = subprocess.run(
            ["git", "-C", str(origin), "show", f"{branch}:index.html"],
            check=True, capture_output=True, text=True).stdout
        check(f"images/{filename}" in pushed, "the remote's index.html has the new photo")
        check("id: 'peacock-blue-test-bow'" in pushed, "the remote's index.html has the new product")

        pushed_theme = subprocess.run(
            ["git", "-C", str(origin), "show", f"{branch}:video/src/theme.ts"],
            check=True, capture_output=True, text=True).stdout
        check(f'image: "{filename}"' in pushed_theme, "the remote's film list has the new scene")

        blob = subprocess.run(
            ["git", "-C", str(origin), "cat-file", "-s", f"{branch}:images/{filename}"],
            check=True, capture_output=True, text=True).stdout.strip()
        check(int(blob) > 1000, f"the photo itself was pushed ({int(blob)//1024} KB)")

        after_images = len(list((repo.path / "images").glob("*.jpg")))
        check(after_images == before_images + 1, "exactly one photo was added")

        # --- the site still parses as one product per photo ---
        ids = pushed.count("      image: 'images/")
        check(ids == after_images, f"every photo still has exactly one card ({ids})")

        # --- a second upload of the same name doesn't overwrite the first ---
        slug2 = unique_slug(slugify("Peacock Blue Test Bow"), repo.path / "images")
        check(slug2 == "peacock-blue-test-bow-2", "a repeated name gets its own file")

        # --- undo ---
        subject, undo_sha = repo.revert_last_bot_commit()
        check("Peacock Blue" in subject, "undo reports what it undid")
        reverted = subprocess.run(
            ["git", "-C", str(origin), "show", f"{branch}:index.html"],
            check=True, capture_output=True, text=True).stdout
        check("peacock-blue-test-bow" not in reverted, "undo removes the product from the remote")
        remaining = subprocess.run(
            ["git", "-C", str(origin), "ls-tree", f"{branch}", "images/"],
            check=True, capture_output=True, text=True).stdout
        check(filename not in remaining, "undo removes the photo too")

        # --- a push that races another push still lands ---
        other = tmp / "other"
        subprocess.run(["git", "clone", str(origin), str(other)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(other), "config", "user.email", "t@t"], check=True)
        subprocess.run(["git", "-C", str(other), "config", "user.name", "t"], check=True)
        (other / "SOMEONE_ELSE.md").write_text("landed first\n")
        subprocess.run(["git", "-C", str(other), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(other), "commit", "-m", "someone else"],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(other), "push"], check=True, capture_output=True)

        (repo.path / "images" / "race.jpg").write_bytes(fake_photo(400, 400))
        race_sha = repo.commit_and_push("Add a piece during a race")
        check(bool(race_sha), "a push that lost a race is rebased and retried")
        final = subprocess.run(["git", "-C", str(origin), "ls-tree", f"{branch}"],
                               check=True, capture_output=True, text=True).stdout
        check("SOMEONE_ELSE.md" in final, "the other person's commit survived the race")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} failed")
        return 1
    print("all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
