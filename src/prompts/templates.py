"""Dynamic prompt templates for driving the Zork-playing agent."""
from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from game_manager.manager import GameState


def _format_history(history: List[dict], max_turns: int = 5) -> str:
    if not history:
        return "(no previous turns)"

    recent = history[-max_turns:]
    lines = []
    for entry in recent:
        command = entry.get("command", "?")
        observation = entry.get("observation", "")
        # if len(observation) > 400:
        #     observation = observation[:400] + " ..."
        lines.append(f"Command: {command}\nObservation: {observation}")
    return "\n\n".join(lines)


def build_prompt(game_state: "GameState", model_name: str) -> str:
    """Construct a concise prompt summarizing the current game state.

    The prompt instructs the model to emit exactly one command for Zork I. It is
    intentionally compact to keep token counts small while still providing
    useful context (score, inventory, recent history).
    """

    history_block = _format_history(game_state.history)
    inventory_text = ", ".join(game_state.inventory) if game_state.inventory else "unknown"
    score_text = game_state.score if game_state.score is not None else "unknown"

    prompt = (
        "You are playing the classic text adventure game Zork I. Respond with "
        "exactly one valid in-game command. Do not explain, narrate, or include "
        "quotes, code fences, or role statements.\n"
        f"Model: {model_name}. Current score: {score_text}. Inventory: {inventory_text}.\n"
        "Recent turns:\n"
        f"{history_block}\n"
        "Output a single text-adventure command only."
    )
    return prompt
