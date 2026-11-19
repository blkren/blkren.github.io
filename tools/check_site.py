"""Site checks to run before every commit: python tools/check_site.py

Checks links, headings, metadata, the LinkedIn calls to action, shared header and footer,
and house style (no em dashes, UK spelling, no banned words). Standard library only.
Exits with code 1 if anything fails."""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINKEDIN = "https://www.linkedin.com/in/chelseaalagoa/"

# Every URL linked from the CV and applications. These must always resolve.
PUBLISHED_URLS = [
    "",
    "retention-and-churn/ai-agent-health-score/",
    "retention-and-churn/health-score-model/",
    "ai-workflows/account-brief-generator/",
    "cs-operations/golive-copilot/",
    "cs-operations/health-score-pipeline/",
    "business-cases-and-roi/compliance-value-model/",
]
BANNED = ["game-changing", "game changing", "revolutionary", "unlock"]
EM_DASH = "\u2014"
US_SPELLINGS = ["organization", "organize", "optimize", "analyze", "color ", "colors", "behavior", "favorite",
                "prioritize", "realize", "recognize", "modeling", "center ", "catalog ", "license "]
STYLE_SKIP = {"assets/fonts/OFL.txt"}

problems = []
warnings = []


def fail(where, msg):
    problems.append(f"{where}: {msg}")


def warn(where, msg):
    warnings.append(f"{where}: {msg}")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.headings, self.links, self.ids, self.text = [], [], set(), []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self._skip += 1
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        if "id" in a:
            self.ids.add(a["id"])
        for key in ("href", "src"):
            if key in a and tag in ("a", "link", "script", "img"):
                self.links.append(a[key])

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)


def tracked_text_files():
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard"],
                         capture_output=True, text=True, check=True).stdout.split()
    exts = {".html", ".md", ".css", ".js", ".py", ".txt", ".xml", ".sql", ".csv", ".svg"}
    return [f for f in out if Path(f).suffix in exts and (ROOT / f).exists()]


def chrome(html, tag):
    m = re.search(rf"<{tag}\b.*?</{tag}>", html, re.S)
    if not m:
        return None
    s = m.group(0)
    s = re.sub(r'(href|src)="((?:\.\./)+|/|\./)?', r'\1="', s)  # normalise path prefixes at any depth
    s = re.sub(r'href="#', 'href="', s)
    return s


def main():
    for u in PUBLISHED_URLS:
        if not (ROOT / u / "index.html").exists():
            fail(u or "/", "published URL no longer resolves")

    pages = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
    headers, footers = {}, {}
    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        html = page.read_text(encoding="utf-8")
        p = Page()
        p.feed(html)

        if p.headings.count(1) != 1:
            fail(rel, f"has {p.headings.count(1)} h1 elements, needs exactly 1")
        for a, b in zip(p.headings, p.headings[1:]):
            if b > a + 1:
                fail(rel, f"heading level jumps from h{a} to h{b}")
        for needle, what in (('lang="en-GB"', "lang en-GB"), ("<title>", "title"), ('name="description"', "meta description"),
                             ('rel="canonical"', "canonical URL"), ('property="og:image"', "Open Graph image"),
                             ('class="skip"', "skip link"), ('id="main"', "main target for skip link")):
            if needle not in html:
                fail(rel, f"missing {what}")
        blog = rel.startswith("thinking-out-loud/")
        # The note that organisations, people and figures are fictional, once per page with case study content.
        if rel != "404.html" and not blog and not re.search(r"fictional|invented", html):
            fail(rel, "missing the note that organisations, people and figures are fictional")
        if blog and rel != "thinking-out-loud/index.html":
            if "not the views of any employer" not in html:
                fail(rel, "post is missing the personal reading notes disclaimer")
            src = re.search(r'<aside class="source".*?</aside>', html, re.S)
            if not src or not re.search(r'href="https?://|TODO', src.group(0)):
                fail(rel, "post is missing a linked source (or a TODO for one)")
            if len(re.findall(r"“|&ldquo;|\"[A-Z][^\"<>]{3,}\"", re.sub(r"<[^>]+>", "", html.split('class="prose', 1)[-1]))) > 1:
                warn(rel, "more than one direct quote, check the one-quote-per-source rule")
        for todo in re.findall(r"TODO[^<]*", html):
            warn(rel, todo.strip())

        for link in p.links:
            if link.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            target, _, frag = link.partition("#")
            target = target.partition("?")[0]  # ignore cache-busting versions such as ?v=20261119
            if not target:
                if frag and frag not in p.ids:
                    fail(rel, f"in-page link #{frag} has no target")
                continue
            base = ROOT if target.startswith("/") else page.parent
            path = (base / target.lstrip("/")).resolve()
            if path.is_dir():
                path = path / "index.html"
            if not path.exists():
                fail(rel, f"broken link {link}")

        n = html.count(LINKEDIN)
        if rel == "index.html":
            hero = re.search(r'<section class="shell hero".*?</section>', html, re.S)
            if not hero or LINKEDIN not in hero.group(0):
                fail(rel, "LinkedIn call to action missing from the hero")
        if rel != "404.html" and not blog:
            cta = re.search(r'<section class="cta".*?</section>', html, re.S)
            if not cta or LINKEDIN not in cta.group(0):
                fail(rel, "LinkedIn call to action missing from the closing band")
        foot = re.search(r"<footer.*?</footer>", html, re.S)
        if foot and LINKEDIN in foot.group(0):
            fail(rel, "the footer repeats the LinkedIn link; the call to action band covers it")
        if n > 2:
            fail(rel, f"LinkedIn appears {n} times, keep it to 2 or fewer (hero and closing band)")
        if 'data-to-top' not in html or '<body id="top">' not in html:
            fail(rel, "missing the back to top button or its #top target")
        if "linkedin.com/in/chelseaalagoa\"" in html:
            fail(rel, "uses the old LinkedIn URL without www and trailing slash")

        headers[rel], footers[rel] = chrome(html, "header"), chrome(html, "footer")
        visible = " ".join(p.text).lower()
        for w in US_SPELLINGS:
            if w in visible:
                fail(rel, f"US spelling '{w.strip()}' in visible text")

    for name, group in (("header", headers), ("footer", footers)):
        variants = {}
        for rel, s in group.items():
            if name == "footer":
                # Page-specific notes are allowed to differ; everything else must match.
                s = re.sub(r'<p class="site-footer__note">.*?</p>', "", s or "", flags=re.S)
            s = re.sub(r"\s+", " ", s or "")
            variants.setdefault(s, []).append(rel)
        if len(variants) > 1:
            fail(name, "differs between pages: " + " | ".join(", ".join(v) for v in variants.values()))

    for f in tracked_text_files():
        if f in STYLE_SKIP:
            continue
        text = (ROOT / f).read_text(encoding="utf-8", errors="ignore")
        if EM_DASH in text:
            fail(f, "contains an em dash")
        low = text.lower()
        for w in ([] if f == "tools/check_site.py" else BANNED):
            if w in low:
                fail(f, f"contains banned word '{w}'")

    if warnings:
        print(f"{len(warnings)} to do before publishing:")
        for w in warnings:
            print("  -", w)
    if problems:
        print(f"{len(problems)} problem(s):")
        for pr in problems:
            print("  -", pr)
        sys.exit(1)
    print(f"All checks passed on {len(pages)} pages.")


if __name__ == "__main__":
    main()
