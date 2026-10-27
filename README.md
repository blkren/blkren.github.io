# Chelsea Alagoa · Customer Success portfolio

**Live site: [blkren.github.io](https://blkren.github.io)**

This repository holds my Customer Success portfolio. It is organised by **skill**, not by employer or job application, so you can go straight to the skill you are hiring for.

All organisations, people and figures in these projects are fictional. The methods are the ones I use at work.

## Skill areas

| Folder | Skill | Projects |
| --- | --- | --- |
| [business-cases-and-roi/](business-cases-and-roi/) | Building business cases and showing return on investment | [Compliance Renewal Value Model](business-cases-and-roi/compliance-value-model/) |
| [ai-workflows/](ai-workflows/) | Using AI to speed up Customer Success work | Coming soon |
| [retention-and-churn/](retention-and-churn/) | Spotting churn risk and keeping customers | Coming soon |
| [cs-operations/](cs-operations/) | Processes, reporting and tooling for CS teams | Coming soon |

The home page only shows a skill area once it has a project.

## What's in a project folder

Each project has its own folder inside its skill area:

```
skill-area/
└── project-name/
    ├── index.html   the project page
    ├── data/        the dataset used (CSV)
    └── model/       the working file, for example an Excel model
```

Every project page follows the same layout:

1. **Summary block:** Skill shown, The problem, What I did, Result, Tools used
2. **Full write-up**
3. **Downloads**

## Other files

- [index.html](index.html): the home page, with one card per skill area
- [assets/styles.css](assets/styles.css): the shared styles for every page
- `.nojekyll`: tells GitHub Pages to publish the files exactly as they are, with no build step

## Adding a project

1. Create a folder inside the right skill area, for example `retention-and-churn/health-score-model/`.
2. Copy an existing project's `index.html` into it as a starting point, and keep the summary block at the top.
3. Link the stylesheet with `../../assets/styles.css`, and put data and model files in `data/` and `model/`.
4. Add a card to the home page `index.html`. There is a commented-out card template in the file.
5. Check that every link works, then commit and push. GitHub Pages updates the live site within a few minutes.

This is plain HTML and CSS, with no build tools or frameworks. To preview a page, open it in a browser.
