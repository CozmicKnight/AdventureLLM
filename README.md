# AdventureLLM

Minimal research repo for benchmarking LLMs on the classic text adventure **Zork I**.
The pipeline mirrors the outline timeline: environment adapter → game manager →
prompt builder → LLM runner → logging → analysis. A mock environment keeps the
loop runnable without the external ZorkAPI.

## Setup

- Python **3.11+**
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- OpenAI key (for real LLM calls): set `OPENAI_API_KEY` in your shell or a `.env`.
  The loop falls back to deterministic commands if the key is absent.

## Running an experiment

Use the CLI to run one or more episodes. By default a mock Zork environment is
used; supply `--base-url` to point at a live [ZorkAPI](https://github.com/Aristoddle/ZorkAPI) server.

```bash
PYTHONPATH=src python -m experiments.run_experiment --model gpt-4.1-mini --episodes 1 --max-moves 20
# real API example
PYTHONPATH=src python -m experiments.run_experiment --model gpt-4.1-mini --episodes 1 --max-moves 20 --base-url http://localhost:5000
```

Logs are written to `data/raw_runs/*.csv` (one file per run with headers
`run_id`, `episode_id`, `model_name`, `move_idx`, `command`, `observation`,
`score`, `moves`, `inventory`, `done`, timestamps, and token counts when
available).

## Analysis notebook

`notebooks/analysis.ipynb` loads all CSVs from `data/raw_runs/`, computes simple
aggregates (final score, moves, token usage), and plots score distributions per
model.

## Repo layout

```
src/
  zork_api_adapter/    # ZorkAPI or mock env wrapper
  game_manager/        # episode loop
  prompts/             # dynamic prompt builder
  llm_runner/          # OpenAI (or offline) command generation
  state/               # CSV logging utilities
  experiments/         # CLI entry point
notebooks/             # analysis notebook
docs/                  # technical summary skeleton
```

## Notes

- Designed for quick iteration within an 8-day timeline; components are
  intentionally lightweight and documented with TODO comments for later
  refinement.
- Replace the mock environment with a real ZorkAPI URL once the service is
  reachable.
