"""Simple CSV logging utilities for per-move data."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


DEFAULT_LOG_DIR = Path("data/raw_runs")


@dataclass
class LogManager:
    log_dir: Path = DEFAULT_LOG_DIR
    log_filename: Optional[str] = None

    def __post_init__(self) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        if self.log_filename:
            self.log_path = self.log_dir / self.log_filename
        else:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            self.log_path = self.log_dir / f"run_{timestamp}.csv"
        if not self.log_path.exists():
            self._write_header()

    def _write_header(self) -> None:
        header = [
            "run_id",
            "episode_id",
            "episode_index",
            "model_name",
            "move_idx",
            "command",
            "observation",
            "score",
            "moves",
            "inventory",
            "done",
            "seed",
            "timestamp",
            "tokens_prompt",
            "tokens_completion",
        ]
        with self.log_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)

    def log_move(
        self,
        run_id: str,
        episode_id: str,
        episode_index: Optional[int],
        model_name: str,
        move_idx: int,
        command: str,
        observation: str,
        score: Optional[int],
        moves: Optional[int],
        inventory: Optional[list],
        done: bool,
        seed: Optional[str],
        tokens_prompt: Optional[int],
        tokens_completion: Optional[int],
    ) -> None:
        timestamp = datetime.utcnow().isoformat()
        row = [
            run_id,
            episode_id,
            episode_index if episode_index is not None else "",
            model_name,
            move_idx,
            command,
            observation,
            score,
            moves,
            ";".join(inventory) if inventory else "",
            done,
            seed or "",
            timestamp,
            tokens_prompt if tokens_prompt is not None else "",
            tokens_completion if tokens_completion is not None else "",
        ]
        with self.log_path.open("a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)
