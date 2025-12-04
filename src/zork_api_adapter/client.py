"""Adapter for interacting with the ZorkAPI service or a local mock environment.

The interface is intentionally small so it can be swapped for the real API
without touching the rest of the pipeline. If the remote ZorkAPI is not
reachable in this environment, a deterministic mock is provided to keep the
end-to-end loop runnable.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import uuid
from pprint import pprint as pp

@dataclass
class ZorkStepResult:
    """Standardized step result returned by :class:`ZorkEnv`.

    Attributes
    ----------
    observation: str
        Main text output from the game after the command is applied.
    score: Optional[int]
        Score reported by the environment, if available.
    moves: Optional[int]
        Number of moves reported by the environment, if available.
    inventory: Optional[List[str]]
        Snapshot of inventory items if exposed by the API.
    done: bool
        Whether the game has reached a terminal state. This is inferred when
        explicit signals are missing.
    raw_response: Dict
        Full JSON payload for debugging and downstream analysis.
    """

    observation: str
    score: Optional[int]
    moves: Optional[int]
    inventory: Optional[List[str]]
    done: bool
    raw_response: Dict


class ZorkEnv:
    """Environment wrapper that communicates with the ZorkAPI service.

    Parameters
    ----------
    base_url: str | None
        Base URL of the ZorkAPI server (e.g., ``"http://localhost:5000"``).
        If ``None``, a :class:`MockZorkEnv` is used instead.
    session: requests.Session | None
        Optional session for connection pooling.
    """

    def __init__(self, base_url: Optional[str] = None, session: Optional[object] = None):
        if base_url is None:
            # Defer to mock environment for offline development.
            self._mock = MockZorkEnv()
            self.base_url = None
            self.session = None
        else:
            from requests import Session  # Imported lazily to avoid dependency when mocking.

            self._mock = None
            self.base_url = base_url.rstrip("/")
            self.session = session or Session()

    def new_game(self, email, game) -> str:
        """Start a new game and return its session identifier."""
        if self._mock:
            return self._mock.new_game()

        response = self.session.post(f"{self.base_url}/newGame?email={email}&title={game}", timeout=10)
        response.raise_for_status()
        payload = response.json()
        # The ZorkAPI returns the session ID inside the payload; field name may vary.
        session_id = payload.get("userProfile")
        if not session_id:
            raise ValueError(f"Unexpected newGame payload: {payload}")
        # print(f"sessionID: {session_id}")
        return str(session_id['email'])

    def step(self, email: str, game: str, command: str) -> ZorkStepResult:
        """Send a command to the Zork game and return the parsed result."""
        if self._mock:
            return self._mock.step(email, command)

        response = self.session.post(f"{self.base_url}/action?email={email}&title={game}&action={command}", timeout=10)
        response.raise_for_status()
        payload = response.json()
        # pp(payload)
        print(f"{'-'*50}")
        print(payload['cmdOutput'])
        # print(payload)
        return self._parse_response(payload)


    @staticmethod
    def _parse_response(payload: Dict) -> ZorkStepResult:
        """Convert raw ZorkAPI payload into :class:`ZorkStepResult`.

        Notes
        -----
        The upstream API schema is light; we defensively pull the fields we know
        about and set the rest to ``None``. "done" is inferred using the
        ``gameOver`` flag or simple heuristics.
        """

        observation = payload.get("cmdOutput")

        if (observation.lower().find("score") > -1):
            text_start = observation.lower().find("score is ")
            text_end = observation.lower().find(" (")
            score_text = observation[text_start + 9:text_end]

            try: 
                score = int(score_text)
                # print(f"Score: {score}")
            except:
                print(f"Score Text: {score_text}")

            text_start = observation.lower().find("), in ")
            text_end = observation.lower().find(" moves")
            moves_text = observation[text_start + 6:text_end]

            try: 
                moves = int(moves_text)
                # print(f"Moves: {moves}")
            except:
                print(f"Moves Text: {moves_text}")

            payload['score'] = score
            payload['moves'] = moves

        else:
            score = 0
            moves = 0
            payload['score'] = 0
            payload['moves'] = 0
            # if "scores" in payload:
            #     score = payload.get("score")
            #     moves = payload.get("moves")
            # else:
                # payload['scores'] = 0
                # payload['moves'] = 0
                # score = 0
                # moves = 0
            # print(f"Score: {score}")
            # print(f"Moves: {moves}")


        inventory = payload.get("inventory")
        game_over_flag = payload.get("gameOver") or payload.get("done")

        # observation_lower = observation.lower()
        inferred_done = False
        if observation:
            terminal_strings = [
                "****  You have died  ****",
                "game over",
                "you have won",
                "the end",
                "would you like to restart",
            ]
            inferred_done = any(key in observation for key in terminal_strings)

        # A perfect score in Zork I is 350; treat that as a win if exposed.
        score_reached_cap = isinstance(score, int) and score >= 350

        done = bool(game_over_flag) or inferred_done or score_reached_cap

        return ZorkStepResult(
            observation=observation,
            score=score if isinstance(score, int) else None,
            moves=moves if isinstance(moves, int) else None,
            inventory=inventory if isinstance(inventory, list) else None,
            done=done,
            raw_response=payload,
        )

    

    """
    --------------------------------------------------
    inventory


    You are carrying:
    A sword
    A brass lantern
    A glass bottle
    The glass bottle contains:
        A quantity of water
    A brown sack
    A leaflet
    """

    # def parse_score(response) -> int:

    #     """
    #     score
    #     Your score is 0 (total of 350 points), in 10 moves.
    #     This gives you the rank of Beginner.
    #     """

    #     score_text_start = response.lower().find("score is ")
    #     score_text_end = response.lower().find("()")
    #     score_text = response[score_text_start + 10:score_text_end]

    #     try: 
    #         score = int(score_text)
    #         print(f"Score: {score}")
    #     except:
    #         print(f"Score Text: {score_text}")
        
    #     return 0
    
class MockZorkEnv:
    """Deterministic offline mock of the Zork environment.

    This keeps the development loop running without external network calls.
    It simulates simple state transitions and marks the game done after a
    small number of moves or if the agent sends a quit command.
    """

    def __init__(self):
        self.sessions: Dict[str, Dict] = {}

    def new_game(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "moves": 0,
            "score": 0,
            "inventory": ["brass lantern"],
            "done": False,
        }
        return session_id

    def step(self, session_id: str, command: str) -> ZorkStepResult:
        state = self.sessions.get(session_id)
        if state is None:
            raise ValueError(f"Unknown session_id: {session_id}")

        state["moves"] += 1
        observation = self._render_observation(command, state)

        # Simple progression: increase score on verbs like "take" or "open".
        if any(keyword in command.lower() for keyword in ["take", "open", "light", "inventory"]):
            state["score"] += 5

        # Terminal if moves exceed 8 or command asks to quit.
        if state["moves"] >= 8 or command.strip().lower() in {"quit", "exit"}:
            state["done"] = True

        payload = {
            "text": observation,
            "score": state["score"],
            "moves": state["moves"],
            "inventory": state["inventory"],
            "gameOver": state["done"],
        }
        return ZorkEnv._parse_response(payload)

    @staticmethod
    def _render_observation(command: str, state: Dict) -> str:
        templates = [
            "You are standing in a mock forest. Paths lead in all directions.",
            "A small mailbox is here. It seems slightly ajar.",
            "There is a grating in the ground, locked tight.",
            "You are inside a mock house with a dusty table.",
        ]
        snippet = templates[state["moves"] % len(templates)]
        return f"Command '{command}' processed. {snippet} (mock turn {state['moves']})."
