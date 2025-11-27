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
            "model_name",
            "move_idx",
            "command",
            "observation",
            "score",
            "moves",
            "inventory",
            "done",
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
        model_name: str,
        move_idx: int,
        command: str,
        observation: str,
        score: Optional[int],
        moves: Optional[int],
        inventory: Optional[list],
        done: bool,
        tokens_prompt: Optional[int],
        tokens_completion: Optional[int],
    ) -> None:
        timestamp = datetime.utcnow().isoformat()
        row = [
            run_id,
            episode_id,
            model_name,
            move_idx,
            command,
            observation,
            score,
            moves,
            ";".join(inventory) if inventory else "",
            done,
            timestamp,
            tokens_prompt,
            tokens_completion,
        ]
        with self.log_path.open("a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)
