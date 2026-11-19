# Chelsea Alagoa · Technical Customer Success portfolio

**Live site: [blkren.github.io](https://blkren.github.io)**

This repository holds my Technical Customer Success portfolio. It is organised by **skill**, not by employer or job application, so you can go straight to the skill you are hiring for.

All organisations, people and figures in these projects are fictional.

## Skill areas

| Folder | Skill | Projects |
| --- | --- | --- |
| [retention-and-churn/](retention-and-churn/) | Spotting churn risk and keeping customers | [AI Agent Customer Health Score](retention-and-churn/ai-agent-health-score/), and the SaaS version it extends: [Customer Health Score Model](retention-and-churn/health-score-model/) |
| [ai-workflows/](ai-workflows/) | Using AI to speed up Customer Success work | [Pre-call Account Briefs with Claude](ai-workflows/account-brief-generator/) |
| [cs-operations/](cs-operations/) | Processes, reporting and tooling for CS teams | [AI Agent Go-live Kit](cs-operations/golive-copilot/), [Health Score Pipeline: from Excel to SQL and Slack](cs-operations/health-score-pipeline/) |
| [business-cases-and-roi/](business-cases-and-roi/) | Building business cases and showing return on investment | [Compliance Renewal Value Model](business-cases-and-roi/compliance-value-model/) |

The home page only shows a skill area once it has a project, in the order above.

## What's in a project folder

Each project has its own folder inside its skill area:

```
skill-area/
└── project-name/
    ├── index.html   the project page
    ├── data/        the dataset used (CSV)
    ├── model/       the working file, for example an Excel model
    ├── code/        scripts and SQL, for projects that run as code
    └── examples/    sample output, for projects that generate something
```

Every project page follows the same layout:

1. **Title and the so what:** the result in one sentence
2. **Where the chain broke:** a five-stage strip (Buy, Onboard, Adopt, Realise value, Renew) with the break marked
3. **At a glance:** Challenge, Approach, Impact, Skills shown, Tools, then key figures
4. **Full write-up and downloads**
5. **Call to action:** message me on LinkedIn, then related case studies

## Thinking Out Loud

[thinking-out-loud/](thinking-out-loud/) holds my reading notes: short reflections on the articles, research and talks I use for professional development. Each post has its own folder (`thinking-out-loud/post-name/index.html`) and the same sections: why I picked it up, what it says in brief, what stayed with me, how it applies in professional services and in a tech role, and what I'm still thinking about.

To add a post: copy an existing post's folder, change the title, date, reading time, "In short", tags, source and body, then add it to the top of the list on `thinking-out-loud/index.html`, update the newer and older links on its neighbours, and add it to `sitemap.xml`. Source material is never copied into the repository: summarise in your own words, with at most one short credited quote per source.

## Other files

- [index.html](index.html): the home page, with the value chain, headline figures and one card per project, filterable by skill
- [404.html](404.html): the page GitHub Pages shows for any broken link. It uses root-relative links (`/...`)
- [assets/css/site.css](assets/css/site.css): the one stylesheet for every page, built on colour and type tokens with light and dark themes
- [assets/js/site.js](assets/js/site.js): progressive enhancement only (theme toggle, chain animation, figures, filters, reading progress). Every page works without it
- [assets/fonts/](assets/fonts/): Source Serif 4, self-hosted, with its licence (SIL Open Font License 1.1)
- [assets/img/](assets/img/): favicon and the image used for link previews
- `sitemap.xml` and `robots.txt`: for search engines. Add new pages to the sitemap
- `.nojekyll`: tells GitHub Pages to publish the files exactly as they are, with no build step
- `.gitignore`: keeps local script output (`outputs/`) out of the repository

## Adding a project

1. Create a folder inside the right skill area, for example `retention-and-churn/health-score-model/`.
2. Copy an existing project's `index.html` into it as a starting point. Keep the header, footer and `<head>` exactly as they are, and change the title, description, canonical URL, the stage marked `is-break`, the summary and the write-up.
3. Put data and model files in `data/` and `model/`, and any scripts in `code/`. Script output goes in `outputs/`, which git ignores.
4. Add a card to the `cards` list on the home page, with `data-skill-card` set to its skill (`retention`, `ai`, `ops` or `roi`), and update the count on that skill's filter button. Add the page to `sitemap.xml` and the list in `404.html`.
5. Run `python tools/check_site.py` to check links, headings, the LinkedIn calls to action and house style, then commit and push. GitHub Pages updates the live site within a few minutes.

This is plain HTML, CSS and a small script, with no build tools or frameworks. To preview the site, run `python -m http.server` in the repository folder and open http://localhost:8000.
