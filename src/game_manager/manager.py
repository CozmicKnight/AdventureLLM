"""Episode manager that connects the environment, prompts, LLMs, and logging."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import uuid

from prompts.templates import build_prompt
from llm_runner.runner import generate_action, LLMGeneration
from state.logger import LogManager
from zork_api_adapter.client import ZorkEnv, ZorkStepResult

from time import sleep


@dataclass
class EpisodeResult:
    model_name: str
    episode_id: str
    final_score: Optional[int]
    moves: int
    ended_naturally: bool
    log_path: Path


@dataclass
class GameState:
    session_id: str
    history: List[Dict]
    score: Optional[int] = None
    moves: int = 0
    inventory: Optional[List[str]] = None

    def update(self, result: ZorkStepResult, command: str) -> None:
        self.history.append({"command": command, "observation": result.observation})
        self.score = result.score if result.score is not None else self.score
        self.moves = result.moves if result.moves is not None else self.moves + 1
        self.inventory = result.inventory if result.inventory is not None else self.inventory


class GameManager:
    """Runs a full Zork episode end-to-end."""

    def __init__(self, env: ZorkEnv, log_manager: Optional[LogManager] = None):
        self.env = env
        self.log_manager = log_manager or LogManager()

    def run_episode(
        self,
        model_name: str,
        max_moves: int,
        run_id: str,
        email: str,
        game: str,
        episode_index: int | None = None,
        seed: str | None = None,

    ) -> EpisodeResult:
        session_id = self.env.new_game(email, game)
        episode_id = str(uuid.uuid4())
        state = GameState(session_id=session_id, history=[])
        last_step: Optional[ZorkStepResult] = None

        for move_idx in range(max_moves):
            prompt = build_prompt(state, model_name=model_name)
            generation: LLMGeneration = generate_action(model_name=model_name, prompt=prompt)
            command = generation.action
            sleep(1)
            step_result = self.env.step(email, game, command)
            state.update(step_result, command)
            last_step = step_result

            self.log_manager.log_move(
                run_id=run_id,
                episode_id=episode_id,
                episode_index=episode_index,
                model_name=model_name,
                move_idx=move_idx,
                command=command,
                observation=step_result.observation,
                score=step_result.score,
                moves=step_result.moves,
                inventory=step_result.inventory,
                done=step_result.done,
                seed=seed,
                tokens_prompt=generation.tokens_prompt,
                tokens_completion=generation.tokens_completion,
            )

            if step_result.done:
                break

        ended_naturally = bool(last_step and last_step.done)
        final_score = state.score
        return EpisodeResult(
            model_name=model_name,
            episode_id=episode_id,
            final_score=final_score,
            moves=state.moves,
            ended_naturally=ended_naturally,
            log_path=self.log_manager.log_path,
        )
