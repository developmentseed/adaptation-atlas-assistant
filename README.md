# Adaptation Atlas Co-pilot

We're going to develop a standalone app that will generate visualizations and text summaries from a user's natural language prompt.
These visualizations and summaries will be modeled after the stories already in-use on the [Adaptation Atlas](https://adaptationatlas.cgiar.org/).

We track our work on the [project board](https://github.com/orgs/developmentseed/projects/158).

## Development

Get [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```sh
git clone git@github.com:developmentseed/adaptation-atlas-co-pilot.git
cd adaptation-atlas-co-pilot
uv sync
```

We use [ruff](https://github.com/astral-sh/ruff) for formatting and linting:

```sh
uv run ruff check --fix
uv run ruff format
```
