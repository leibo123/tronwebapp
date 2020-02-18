import time
from tronproblem import TronProblem
import copy, argparse, signal
from collections import defaultdict
import support
import sys, os
import traceback


def run_game(
    asp, bots, game_name, visualizer=TronProblem.visualize_state, max_wait=0.3
):
    """
    Inputs:
        - asp: an adversarial search problem
        - bots: a list in which the i'th element is the bot for player i
        - visualizer (optional): a void function that takes in a game state
          and does something to visualize it. If no visualizer argument is
          passed, run_game will not visualize games.

    Runs a game and outputs the evaluation of the terminal state.
    """

    if not visualizer == None:
        orig_stdout = sys.stdout
        f = open("gamefiles/" + game_name, "w")
        sys.stdout = f

    state = asp.get_start_state()
    if not visualizer == None:
        visualizer(state)

    sys.stdout = open(os.devnull, "w")  # disable printing
    # decisions, errors, timeouts
    metadata = [[0, 0, 0, ""]] * len(bots)
    while not (asp.is_terminal_state(state)):
        exposed = copy.deepcopy(asp)
        metadata[state.ptm][0] += 1
        try:
            signal.signal(signal.SIGALRM, support.timeout_handler)
            signal.setitimer(signal.ITIMER_REAL, max_wait)
            try:
                # run AI
                decision = bots[state.ptm].decide(exposed)
                signal.setitimer(signal.ITIMER_REAL, 0)
            except Exception:
                signal.setitimer(signal.ITIMER_REAL, 0)
                metadata[state.ptm][1] += 1
                if metadata[state.ptm][1] == 1:
                    metadata[state.ptm][3] = "\n".join(
                        clean_error(traceback.format_exc())
                    )
                decision = "U"
        except support.TimeoutException:
            signal.setitimer(signal.ITIMER_REAL, 0)
            metadata[state.ptm][2] += 1
            decision = "U"

        available_actions = asp.get_available_actions(state)
        if not decision in available_actions:
            decision = list(available_actions)[0]

        result_state = asp.transition(state, decision)
        asp.set_start_state(result_state)

        state = result_state
        if not visualizer == None:
            visualizer(state)

    sys.stdout = sys.__stdout__  # restore printing
    if not visualizer == None:
        sys.stdout = orig_stdout
        f.close()

    return asp.evaluate_state(asp.get_start_state()), metadata


def clean_error(message):
    """
    Removes lines related to the grader from the error message so it can be shown to students.
    """
    if not message:
        return []

    lines = filter(lambda l: l, message.split("\n"))
    line_iterator = iter(lines)
    # The first line starts with Traceback, we keep track of it here
    traceback_line = next(line_iterator)
    new_lines = []
    for line in line_iterator:
        if "File " in line:
            first_quote = line.index('"')
            second_quote = line.index('"', first_quote + 1)
            path = line[first_quote + 1 : second_quote]
            path_list = path.split("/")
            if (
                "grader" in path_list
                or "auto_grader" in path_list
                or "submission_report.py" in path_list
            ):
                new_lines.append(None)
                # skip a line
                next(line_iterator)
                continue
            else:
                new_lines.append(
                    line[:first_quote]
                    + '"'
                    + os.path.basename(path)
                    + line[second_quote:]
                )
                continue
        new_lines.append(line)

    # Remove redacted messages from beginning of stack trace
    while new_lines and new_lines[0] is None:
        new_lines.pop(0)
    if len(new_lines) <= 1:
        new_lines = [
            "This error appears to be located entirely within the grading script(s).",
            "This means you probably have a function outputting the wrong type.",
        ]
    else:
        new_lines = [traceback_line] + [
            "<Redacted: error occurs within grading script(s)>" if l is None else l
            for l in new_lines
        ]

    return new_lines
