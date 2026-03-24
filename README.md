# Carbon Farming Knowledge Map

Interactive study map for carbon farming in Scotland. Built with Jekyll for GitHub Pages.

## Setup

1. Create a new GitHub repository called `carbon-farming`
2. Push these files to the `main` branch
3. Go to **Settings → Pages → Source** and select `main` branch
4. Your site will be live at `https://yourusername.github.io/carbon-farming/`

## Editing notes

Each node links to a markdown file in `notes/`. Edit them directly on GitHub or clone the repo and edit locally.

To add a new node, you need to:
1. Create a new `.md` file in `notes/` with the correct front matter (`layout`, `title`, `node`)
2. Add the node to the `items` array in `_includes/diagram.html`
3. Add any edges to the `edges` array in `_includes/diagram.html`

## Local preview

```
gem install jekyll bundler
bundle init
bundle add github-pages
bundle exec jekyll serve
```

Then open `http://localhost:4000/carbon-farming/`

## Structure

```
_config.yml              Jekyll config
_layouts/default.html    Page template (diagram + content)
_includes/diagram.html   The interactive SVG diagram
index.md                 Landing page
notes/                   One markdown file per topic
```
