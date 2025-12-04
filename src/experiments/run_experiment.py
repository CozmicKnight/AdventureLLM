"""CLI for running one or more Zork episodes with a chosen model."""
from __future__ import annotations

import argparse
import uuid

from game_manager.manager import GameManager
from state.logger import LogManager
from zork_api_adapter.client import ZorkEnv

from pprint import pprint as pp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Zork LLM experiments")
    parser.add_argument("--model", required=True, help="Model name (e.g., gpt-4.1-mini)")
    parser.add_argument("--episodes", type=int, default=1, help="Number of episodes to run")
    parser.add_argument("--max-moves", type=int, default=50, help="Max moves per episode")
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Base URL for ZorkAPI. If omitted, the mock environment is used.",
    )
    parser.add_argument(
        "--log-filename",
        type=str,
        default=None,
        help="Optional log filename (stored in data/raw_runs)",
    )
    parser.add_argument(
        "--seed",
        type=str,
        default=None,
        help="Optional run-level seed recorded in the log for reproducibility",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    log_manager = LogManager(log_filename=args.log_filename)
    env = ZorkEnv(base_url=args.base_url)
    manager = GameManager(env=env, log_manager=log_manager)

    run_id = str(uuid.uuid4())
    results = []
    for episode_idx in range(args.episodes):
        result = manager.run_episode(
            model_name=args.model,
            max_moves=args.max_moves,
            run_id=run_id,
            email="john@eley.net",
            game="zork1",
            episode_index=episode_idx,
            seed=args.seed,
        )
        results.append(result)

    print("=== Run summary ===")
    pp(results)
    for idx, res in enumerate(results, start=1):
        end_state = "natural" if res.ended_naturally else "max_moves"
        print(f"Episode {idx}: score={res.final_score} moves={res.moves} end={end_state} log={res.log_path}")


if __name__ == "__main__":
    main()
