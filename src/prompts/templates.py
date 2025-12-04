"""Dynamic prompt templates for driving the Zork-playing agent."""
from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from game_manager.manager import GameState


def _format_history(history: List[dict], max_turns: int = 500) -> str:
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
        "You are playing the classic text adventure game Zork I. Respond with exactly one valid in-game command. Do not explain, narrate, or include quotes, code fences, or role statements. "
        "The \'north\' command moves you in the north direction. "
        "The \'south\' command moves you in the south direction. "
        "The \'east\' command moves you in the east direction. "
        "The \'west\' command moves you in the west direction. "
        "The \'up\' command will move you up direction. "
        "The \'down\' command will move you in the down direction. "
        "The \'look\' command will give you a description of the area around you. "
        "The \'score\' command will display your current score. Check your score periodically. "
        "The \'diagnose\' will describe your current health. "
        "The \'climb\' command will allow you to climb up. It is not useful if there is no object to climb. "
        "The \'enter\' will move you into a location, if possible. "
        "The \'in\' will move you into a location, if possible. "
        "The \'out\' will move you into a location, if possible. "
        "The \'get (item)\' command will allow you to pick up the named item and places it in your inventory. "
        "The \'take (item)\' command will allow you to pick up the named item and places it in your inventory. "
        "The \'grab (item)\' command will allow you to pick up the named item and places it in your inventory. "
        "The \'get all\' command will allow you to pick up all available items in the area and places them in your inventory. "
        "The \'take all\' command will allow you to pick up all available items in the area and places them in your inventory. "
        "The \'grab all\' command will allow you to pick up all available items in the area and places them in your inventory. "
        "The \'attack (creature) with (item)\' command will attack the named creature with the named item. It is best to use an item that is a weapon. "
        "The \'throw (item) at (location)\' causes you to throws the named item item at the named location. "
        "The \'open (container)\' opens the named container, whether it is in the room or your inventory. "
        "The \'read (item)\' provides you a description of what is written on readable item. "
        "The \'drop (item)\' removes item from your inventory and places it in current room. "
        "the \'put (item) in (container)\' removes the named item from your inventory and places it in the named container. "
        "The \'move (object)\' command will move the named object. You may be able to move an object that cannot be picked up. "
        "The \'examine (object)\' provides more detail about the named object or item or location. "
        "The \'inventory\' displays contents of your inventory. "
        "The \'eat (item)\' command causes you to consume the named item (specifically food). "
        "The \'close (door)\' command will close named door. "
        "Here some clues to help you start to play: "
        "The house has one window that you can open and use it to enter the house. "
        "Use the examine command to analyze each objects you encounter. if you cannot pickup an item, you may be able to move it. "
        "The goal of the game is to get a score of 350 in as few moves as possible. \n"
        # "After every 5 commands, check your progress with the score command. "
        # "If you have the \'ZORK owner\'s manual\' in your inventory, reading it might help understand gameplay.\n"
        # f"Model: {model_name}. Current score: {score_text}. Inventory: {inventory_text}.\n"
        "Recent turns:\n"
        f"{history_block}\n"
        # "Output a single text-adventure command only."
    )
    return prompt

