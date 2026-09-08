# Kazakh Threads Skills

*[Қазақша](README.md) · **English***

**9 Claude Code and Codex skills for writing Threads posts in Kazakh.**
They draft the post, strip Russian calques and officialese, catch spelling
errors invisible to the eye, and plan a week of content. Optionally, they
publish through the official Threads API and pull the numbers back.

Not a translation of an English bundle: built around four problems that are
specific to Kazakh. No separately trained model either — Claude is given a
Kazakh-specific knowledge base and checkers that actually run.

[![CI](https://img.shields.io/github/actions/workflow/status/kazprose/threads-qaz/tekseru.yml?branch=main&label=tests&color=22C55E)](https://github.com/kazprose/threads-qaz/actions/workflows/tekseru.yml)
![License](https://img.shields.io/badge/License-MIT-22C55E.svg)
![Dependencies](https://img.shields.io/badge/dependencies-none-111827.svg)

---

## Why this exists

Four things break consistently when an AI writes Kazakh:

| Problem | Example | Consequence |
|---|---|---|
| **Homoglyphs** | `бiр` (Latin i) vs `бір` (Cyrillic і) | search never finds it, hashtags die |
| **Vowel harmony** | `дедлайнге` (should be `дедлайнға`) | wrong suffix on a loanword |
| **Russian calques** | «мақсатымыз болып табылады» | reads like a government notice |
| **Register mixing** | «сен» and «сіз» in one post | the most visible artificiality |

The first one is the worst because it is **invisible**. Latin `i` and Cyrillic
`і` render identically. You are confident the post is correct; search
disagrees.

```
$ python3 -m lib.emle "Бiз бүгін жаңа фичаны шығардық. #қазақстан #стартап"

Таңба: 60/500 | сөз: 8 | хэштег: 2 | қазақ әрпінің үлесі: 15.1%

[ҚАТЕ] гомоглиф: «Бiз» — кирилл сөзі, бірақ ішінде латын әрпі бар:
       «i» → «і». Дұрысы: «Біз».
[ҚАТЕ] хэштег: 2 хэштег. Threads біреуін ғана қабылдайды.
```

Detection runs in both directions: `Бiз` → `Біз` (Latin intruder in a
Cyrillic word) and `Clаudе` → `Claude` (Cyrillic intruder in a Latin word).
Pure Latin words (`Claude`, `AI`, `startup`) are left alone — that is
legitimate code-switching, not an error.

### This found a real bug in real infrastructure

`hunspell-kk` is the Kazakh orthographic dictionary used by LibreOffice and
OpenOffice. Scanning its 54,063 entries with this project's checker found
**16 words written with Latin letters** — all names of well-known Kazakh
writers:

| In the dictionary | Intruder | Correct |
|---|---|---|
| `Бейiмбет` | `i` U+0069 LATIN SMALL I | Бейімбет |
| `Сейiт` | `i` U+0069 | Сейіт |
| `Iсмет` | `I` U+0049 LATIN CAPITAL I | Ісмет |
| `Aманжол` | `A` U+0041 LATIN CAPITAL A | Аманжол |

The correctly spelled forms are **not in the dictionary at all**. So the
spellchecker flags the correct spelling as an error and accepts the corrupted
one. A dictionary teaching the wrong spelling.

## Install

```
/plugin marketplace add kazprose/threads-qaz
/plugin install threads-qazaqsha@threads-qazaqsha
```

Or on claude.ai / Claude Desktop: **Skills → Add from GitHub →
`kazprose/threads-qaz`**

Or just clone it:

```bash
git clone https://github.com/kazprose/threads-qaz.git
cd threads-qaz
```

No `pip install` needed — `lib/` uses only the standard library.

## The nine skills

| Skill | What it does |
|---|---|
| **threads-profil** | Voice profile: who you are, your audience, «сен» or «сіз», words you never use. Filled once, read by the rest |
| **threads-post-jazu** | Drafts a post or thread using one of 13 hook formulas picked by goal |
| **threads-redaktor** | Strips officialese, calques and AI tells; `--mode audit` checks without rewriting |
| **threads-emle** | Homoglyphs (both directions), vowel harmony, alphabet, hashtags, QazLat 2021 transliteration |
| **threads-hook-taldau** | Reverse-engineers someone else's post and says what *cannot* be copied |
| **threads-jauap** | Reply or quote post, and decides which one is right |
| **threads-jospar** | Weekly plan: pillars, formulas, timing, engagement quota |
| **threads-beiimdeu** | Adapts content from another platform or language. A rewrite, not a translation |
| **threads-natije** | Logs what you published and shows which format actually works for *your* audience |

## Three formulas that only exist here

Of the 13 hook formulas, three have no equivalent in other languages:

- **Q7 — a language observation.** Something odd about a word or a
  translation. The single most reliable topic in Kazakh social media:
  language is common property, everyone has their own version, and every
  version is a reply.
- **Q8 — an untranslatable concept.** A word Kazakh has and other languages
  don't. Travels well as a quote post.
- **Q9 — between two languages.** The concrete friction of living between
  Kazakh and Russian/English. Most of the audience is in exactly that spot.

## Honesty about evidence

There is **no measured corpus of Kazakh-language Threads posts**. So this
repository does not quote a number like "the average reach of a Kazakh post
is X". Anyone who does is making it up.

Every claim is tagged with its source: `[платформа]` — a hard Threads limit;
`[редактура]` — Kazakh editorial practice; `[болжам]` — a hypothesis worth
testing.

These skills do **not** promise to beat AI detectors, and do not try. On
post-length text detector scores are noise, and light rewriting does not fool
them. The goal is different: not reading as foreign to a human reader.

The hook formulas and the algorithm notes are still **hypotheses**. The only
way to change that is measurement — which is what `threads-natije` is for.

## Automation (optional)

Nothing is automated by default.

**Pull statistics automatically.** With `THREADS_TOKEN` configured, the
official Threads API fills the journal for you. Setup requires registering a
Meta app; it works for **your own account** only.

**Publish without approval.** With `THREADS_AVTO=1`, a draft publishes
itself — but only one that passed every check:

```
checks clean  → published
one error     → stops, explains why, hands you a copy-paste block
```

A rejected draft is **never sent to any backend**. The point of automation is
not sitting through every post; a broken post going out automatically would
defeat that point.

Replies and quote posts are never auto-published: they attach to someone
else's post, and hitting the wrong target is a real risk.

## The library on its own

`lib/` works without the skills:

```python
import sys; sys.path.insert(0, "threads-qaz")
from lib import tolyq, gomoglif_tuzetu, undestik_tekseru, latynga

print(tolyq("post text"))               # spelling + purity + harmony + profile
print(gomoglif_tuzetu("Бiз"))           # → Біз
print(gomoglif_tuzetu("Clаudе"))        # → Claude
print(undestik_tekseru("дедлайнге"))    # → дедлайнға
print(latynga("тіл"))                   # tıl — і → ı, и → i (they differ)
```

```bash
python3 -m lib.emle "text"       # homoglyphs, alphabet, Threads limits
python3 -m lib.kalka "text"      # calques, officialese, structure
python3 -m lib.undestik "text"   # vowel harmony
python3 -m lib.audit "text"      # all of it, exit code 0/1
```

## Security

The project touches an API token and can publish publicly on your behalf.
See [`SECURITY.md`](SECURITY.md). The short version: request the least
privilege (skip `threads_content_publish` unless you want auto-publish),
never paste the token into chat, and note that there is no telemetry — the
journal and profile stay on your machine.

## Contributing

The most useful contribution is adding entries to the calque dictionary in
`lib/kalka.py`. Each entry needs the Russian original and a concrete
replacement, not just "rewrite this".

Rules that matter: no dependencies in `lib/`, no invented numbers, and skill
descriptions carry Kazakh, English and Russian trigger words. Details in
[`CLAUDE.md`](CLAUDE.md).

```bash
python3 -m unittest discover -s tests    # 107 tests
python3 scripts/siltemelerdi_tekseru.py
python3 scripts/frontmatter_tekseru.py
python3 scripts/eval_tekseru.py
```

## Other Kazakh language resources

This bundle is deliberately dependency-free and includes none of these, but
they go deeper:

| Resource | What it adds | License |
|---|---|---|
| [hunspell-kk](https://github.com/taem/hunspell-kk) | 53k+ stems, real spellchecking | GPL-2.0+ / LGPL-2.1+ / MPL-1.1+ |
| [apertium-kaz](https://github.com/apertium/apertium-kaz) | full morphological analyser | GPL |
| [kaznlp](https://github.com/nlacslab/kaznlp) | tokenisation, morphology, language ID | — |
| [UD_Kazakh-KTB](https://github.com/UniversalDependencies/UD_Kazakh-KTB) | syntactic treebank | CC BY-SA |
| [awesome-kaz-datasets](https://github.com/Allessyer/awesome-kaz-datasets) | catalogue of Kazakh datasets | — |

`lib/emle.py` is rule-based: it catches homoglyphs, alphabet ratio and vowel
harmony, but **does not know whether a word is spelled correctly**. That needs
a hunspell dictionary — the most valuable next step if you are willing to take
on a dependency.

## License

MIT.

Structural idea borrowed from
[sergebulaev/threads-skills](https://github.com/sergebulaev/threads-skills)
(MIT). The content, the library and the hook formulas were written from
scratch for Kazakh.
