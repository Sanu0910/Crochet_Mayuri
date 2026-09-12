"""Tests for the risky half of the bot: editing the site's product lists.

These run against real copies of index.html and video/src/theme.ts, so a
change to either file that would break the bot fails here first.

    cd bot && python test_site_edit.py
"""

import re
import shutil
import sys
import tempfile
from pathlib import Path

from site_edit import (
    SiteEditError,
    insert_into_film,
    insert_into_index,
    product_ids,
    remove_product,
    update_product,
)
from pricing import find_price

REPO = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def check(condition: bool, message: str) -> None:
    if condition:
        print(f"  ok   {message}")
    else:
        print(f"  FAIL {message}")
        FAILURES.append(message)


def fresh(tmp: Path) -> tuple[Path, Path]:
    index = tmp / "index.html"
    theme = tmp / "theme.ts"
    shutil.copy(REPO / "index.html", index)
    shutil.copy(REPO / "video/src/theme.ts", theme)
    return index, theme


def cat_order(index: Path) -> list[str]:
    return re.findall(r"cat: '([a-z]+)'", index.read_text())


def main() -> int:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)

        # --- a category that already has members: group with them ---
        index, theme = fresh(tmp)
        before = len(product_ids(index.read_text()))
        insert_into_index(index, product_id="test-bow", name="Test Bow",
                          cat="bows", desc="A test.", image="test-bow.jpg")
        text = index.read_text()
        check(len(product_ids(text)) == before + 1, "index gains exactly one product")
        check("id: 'test-bow'" in text, "new id lands in index.html")
        check("images/test-bow.jpg" in text, "photo path lands in index.html")
        check("tag: 'Bows'" in text, "card tag comes from the category")

        order = cat_order(index)
        first_bow = order.index("bows")
        check(order[first_bow] == "bows" and order[first_bow + 1] == "bows",
              "new bow sits with the other bows, not at the end")
        check(order[-1] == "hearts", "the hearts entry is still last")

        # --- a category with no members yet: goes at the end ---
        index2, theme2 = fresh(tmp / "b" if (tmp / "b").mkdir() or True else tmp)
        insert_into_index(index2, product_id="test-heartless", name="Nothing Like It",
                          cat="clips", desc="A test.", image="x.jpg")
        check("id: 'test-heartless'" in index2.read_text(), "second insert works on a clean copy")

        # --- duplicate ids are refused ---
        try:
            insert_into_index(index, product_id="test-bow", name="Test Bow",
                              cat="bows", desc="Again.", image="test-bow.jpg")
            check(False, "a duplicate id is refused")
        except SiteEditError:
            check(True, "a duplicate id is refused")

        # --- quotes in a name can't break out of the JS string ---
        index3, theme3 = fresh(tmp)
        insert_into_index(index3, product_id="quoted", name="Mayuri's \"Best\" Bow",
                          cat="bows", desc="It's got 'quotes'.", image="q.jpg")
        text3 = index3.read_text()
        # Double quotes need no escaping inside a single-quoted JS string.
        expected_name = "name: 'Mayuri\\'s \"Best\" Bow'"
        check(expected_name in text3, "single quotes in a name are escaped")
        insert_into_index(index3, product_id="scripty", name="Bow </script><b>x",
                          cat="bows", desc="d", image="s.jpg")
        check("</script>" not in index3.read_text().split("const PRODUCTS")[1].split("];")[0],
              "a caption cannot close the script block")
        check(r"desc: 'It\'s got \'quotes\'.'" in text3, "single quotes in a description are escaped")

        # --- the film list stays in step ---
        insert_into_film(theme, name="Test Bow", cat="bows", image="test-bow.jpg")
        film = theme.read_text()
        check('{ image: "test-bow.jpg", name: "Test Bow", tag: "Bows" },' in film,
              "the film scene list gains the piece")
        tags = re.findall(r'tag: "([A-Za-z ]+)"', film)
        first_bows = tags.index("Bows")
        check(tags[first_bows + 1] == "Bows", "the new film scene sits with the other bows")

        # --- missing markers are a clear error, not a corrupted file ---
        broken = tmp / "broken.html"
        broken.write_text("<html>no markers here</html>")
        try:
            insert_into_index(broken, product_id="x", name="X", cat="bows",
                              desc="d", image="x.jpg")
            check(False, "a file without markers is refused")
        except SiteEditError as exc:
            check("markers" in str(exc), "a file without markers is refused with a clear message")

        # --- prices ---
        for text, want in [
            ("Ocean Scrunchie \u20b9250", "\u20b9250"),
            ("Bow Rs. 1,200", "\u20b91,200"),
            ("Vine 450/-", "\u20b9450"),
            ("Clip INR 99", "\u20b999"),
            ("Set of 3 hearts", None),        # a count, not a price
            ("Bouquet of 5 roses", None),     # likewise
            ("Rose 0", None),                 # zero is not a price
        ]:
            got, rest = find_price(text)
            check(got == want, f"price from {text!r} -> {got!r}")
            if want:
                check(want not in rest, f"price is stripped out of {text!r}")

        index4, theme4 = fresh(tmp)
        insert_into_index(index4, product_id="priced", name="Priced Bow", cat="bows",
                          desc="d", image="p.jpg")
        insert_into_index(index4, product_id="unpriced", name="Unpriced Bow", cat="bows",
                          desc="d", image="u.jpg")
        check("price:" not in index4.read_text(),
              "no price is ever written to the site")

        # --- removing ---
        images = tmp / "imgs"
        images.mkdir(exist_ok=True)
        (images / "p.jpg").write_bytes(b"x" * 100)
        insert_into_film(theme4, name="Priced Bow", cat="bows", image="p.jpg")
        name, image = remove_product(index4, theme4, images, "priced")
        check(name == "Priced Bow", f"remove finds it by id (got {name!r})")
        check("id: 'priced'" not in index4.read_text(), "remove takes it out of index.html")
        check('image: "p.jpg"' not in theme4.read_text(), "remove takes it out of the film list")
        check(not (images / "p.jpg").exists(), "remove deletes the photo file")
        check("id: 'unpriced'" in index4.read_text(), "remove leaves other pieces alone")

        name2, _ = remove_product(index4, theme4, images, "unpriced bow")
        check(name2 == "Unpriced Bow", "remove also matches on the name")

        index5, theme5 = fresh(tmp)
        insert_into_index(index5, product_id="bow-a", name="Rose Bow One", cat="bows",
                          desc="d", image="a.jpg")
        insert_into_index(index5, product_id="bow-b", name="Rose Bow Two", cat="bows",
                          desc="d", image="b.jpg")
        # "rose bow" is nobody's full name but is inside both — refuse rather
        # than pick one, since the wrong guess deletes a photo.
        try:
            remove_product(index5, theme5, images, "rose bow")
            check(False, "an ambiguous partial name is refused")
        except SiteEditError as exc:
            check("matches 2 pieces" in str(exc), "an ambiguous partial name is refused")
        check("id: 'bow-a'" in index5.read_text() and "id: 'bow-b'" in index5.read_text(),
              "an ambiguous remove deletes nothing")
        # An exact name is never ambiguous, even when it sits inside another.
        insert_into_index(index5, product_id="bow-c", name="Rose Bow", cat="bows",
                          desc="d", image="c.jpg")
        removed_name, _ = remove_product(index5, theme5, images, "Rose Bow")
        check(removed_name == "Rose Bow", "an exact name wins over longer ones containing it")

        # --- editing wording after the fact ---
        index6, theme6 = fresh(tmp)
        insert_into_index(index6, product_id="edit-me", name="Typo Bow", cat="bows",
                          desc="Wrong words.", image="e.jpg")
        insert_into_film(theme6, name="Typo Bow", cat="bows", image="e.jpg")
        old_name, new_name = update_product(index6, theme6, "edit-me",
                                            name="Tidy Bow", desc="Better words.")
        text6 = index6.read_text()
        check((old_name, new_name) == ("Typo Bow", "Tidy Bow"), "update reports both names")
        check("name: 'Tidy Bow'" in text6, "the new name lands in index.html")
        check("desc: 'Better words.'" in text6, "the new description lands too")
        check("Typo Bow" not in text6, "the old name is gone from the site")
        check('name: "Tidy Bow"' in theme6.read_text(), "the film scene is renamed too")
        check('image: "e.jpg"' in theme6.read_text(), "the film still points at the same photo")
        check("id: 'edit-me'" in text6, "the id is left alone, so nothing that links to it breaks")

        update_product(index6, theme6, "Tidy Bow", desc="Only the words change.")
        check("name: 'Tidy Bow'" in index6.read_text(), "editing only the description keeps the name")

        try:
            remove_product(index4, theme4, images, "does not exist")
            check(False, "removing something absent is refused")
        except SiteEditError:
            check(True, "removing something absent is refused")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} failed")
        return 1
    print("all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
