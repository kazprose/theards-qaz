# threads-skills қалай жұмыс істейді

Талдау нысаны: https://github.com/sergebulaev/threads-skills (v1.0.20, MIT)

## 1. Не бұл?

Claude Code / Codex үшін **Skills бандлы**. Негізгі мазмұны — markdown
нұсқаулықтар, Python коды жұқа қабат қана (~1300 жол).

```
skills/*/SKILL.md   8 шеберлік (промпт нұсқаулықтары)
references/*.md     ортақ білім базасы (hook формулалары, voice ережелері)
lib/*.py            API клиенттері (Publora, Apify, Pixfaro)
.claude-plugin/     Claude плагин манифесі
.codex-marketplace/ Codex үшін генерацияланған көшірме
scripts/            markdown сілтемелерін тексеру + codex sync
```

Көлемі: ~3600 жол мәтін, оның ~1250-і Python.

## 2. Автоматты іске қосылу механизмі

Әр `SKILL.md` басында YAML frontmatter:

```yaml
---
name: threads-post-writer
description: Draft a single Threads post or a multi-post thread...
             Not for auditing a draft (use threads-humanizer).
---
```

Модель жадында тек `description` жолдары тұрады. Сұраныс сәйкес келгенде
ғана толық файл оқылады — бұл **progressive disclosure**. `description`
ішіндегі "Not for X (use Y)" — шеберліктер шатаспауы үшін жазылған
теріс шекара.

## 3. Үш деңгейлі жариялау (lib/backend_selector.py)

| Деңгей | Шарт | Нәтиже |
|---|---|---|
| Tier 0 | кілт жоқ (әдепкі) | драфт + көшіріп-қою блогы |
| Tier 1 | `PUBLORA_API_KEY` + `THREADS_PLATFORM_ID` | Publora арқылы автопост |
| Tier 2 | `THREADS_SKILLS_CUSTOM_POSTER` | өз скриптіңді шақырады |

`active_backend()` env айнымалыларын тексеріп ең жоғарғысын таңдайды.
Кілтсіз де бәрі істейді.

Ерекше жағдай: басқа адамның постына жауап (reply) және quote post әрқашан
қолмен қойылады — Publora `create-post` бөтен постты нысана ете алмайды.

## 4. Approval gate

`lib/approval.py` → `render_approval_card()` драфтты карточка етіп шығарады
(kind, char count, post count, target URL) және "post / yes" дегенше тоқтайды.

МАҢЫЗДЫ: файлдың өз түсініктемесінде "thin conventions layer, **not runtime
enforcement**" деп жазылған. Яғни бұл техникалық тосқауыл емес, келісім ғана.

## 5. Оқу қабаты (lib/apify_client.py)

Apify скраперлері арқылы нақты Threads деректері:
- `igview-owner~threads-search-scraper` — сұраныс/хэштег бойынша топ посттар
- `apify~threads-profile-api-scraper` — профиль статистикасы, соңғы посттар

In-process LRU кэш (256 жазба, 6 сағат TTL), 429/5xx үшін retry.
Threads лайк басқандар тізімін бермейді — бұл платформа шектеуі.

## 6. 8 шеберлік

| Шеберлік | Қызметі |
|---|---|
| threads-post-writer | 13 hook формуласымен пост/тред жазу |
| threads-humanizer | AI іздерін тазалау + `--mode audit` тексеру |
| threads-hook-extractor | вирусты посттың хугын кері инженерия |
| threads-reply-drafter | жауап / quote post драфты |
| threads-repurposer | басқа платформа контентін бейімдеу |
| threads-content-planner | апталық жоспар |
| threads-profile-optimizer | профиль аудиті мен қайта жазу |
| threads-audience-insights | нақты дерек бойынша аудитория талдауы |

## 7. Мазмұн сапасы

Ең күшті бөлігі — `threads-humanizer` (285 жол). Әр тұжырымның дәлел деңгейі
белгіленген: `[strong]` / `[vendor]` / `[weak]`. n=311 корпус, Spearman
корреляциясы келтірілген. Адал ұстаным: "AI детекторларды алдай алмаймыз,
ешбір өңдеу оны сенімді істемейді".

`references/hook-formulas.md` — 471 жол, 13 формула, әрқайсысында скелет
және мақсат тегі (replies / reposts / likes / quotes).

## 8. Сақтық танытатын тұстар

- **Vendor lock-in**: Publora (ақылы SaaS) — әдепкі жол. Драфт мақұлданғаннан
  кейін жүйе автоматты түрде тіркелу нұсқаулығын шығарады
  (`backend_selector.py`, `manual_mode_message`). Автор Publora-мен байланысты.
- **Жұлдыз сұрау промптқа тігілген**: root `SKILL.md` соңында модельге
  "сессияға бір рет репоны жұлдызшалауды ұсын" деген нұсқау бар.
- **"2026 corpus" деректері** тексерілмеген — авторға сену керек.
- **Сыртқы тәуелділік**: requests, python-dotenv + Apify/Pixfaro/Publora API
  кілттері `.env` файлында.

Қауіпсіздік: жасырын желі шақырулары, обфускация, зиянды prompt injection
табылмады. CI-да `hol-plugin-scanner` (плагин қауіпсіздік сканері, SARIF)
және markdown сілтемелерін тексеретін workflow бар.

## 9. Орнату

```
/plugin marketplace add sergebulaev/threads-skills
/plugin install threads-skills@threads-skills
```

Немесе claude.ai веб: Skills → Add from GitHub → `sergebulaev/threads-skills`.

## 10. Қорытынды

Ең құнды бөлігі — `references/` мен `skills/` ішіндегі мәтіндер. Оларды өз
нишаңа (мысалы, қазақ тіліндегі контентке) бейімдеп қайта жазсаң, дәл сондай
жүйені өзің құра аласың. Архитектурасы қарапайым әрі көшіруге ыңғайлы:
frontmatter + markdown нұсқаулық + жұқа Python клиент.
