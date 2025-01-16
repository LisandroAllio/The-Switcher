import pytest
from schemas.card import MoveType
from core.game_logic.aux.movValidator import is_valid_mov


def test_check_movements():

    no_skip_line_cases = [
        (MoveType.NO_SKIP_LINE, (1, 1), (2, 1), True),
        (MoveType.NO_SKIP_LINE, (1, 1), (1, 2), True),
        (MoveType.NO_SKIP_LINE, (2, 3), (2, 2), True),
        (MoveType.NO_SKIP_LINE, (3, 2), (2, 2), True),
        (MoveType.NO_SKIP_LINE, (2, 2), (2, 2), False),
    ]

    skip_one_line_cases = [
        (MoveType.SKIP_ONE_LINE, (1, 1), (3, 1), True),
        (MoveType.SKIP_ONE_LINE, (1, 1), (1, 3), True),
        (MoveType.SKIP_ONE_LINE, (3, 2), (1, 2), True),
        (MoveType.SKIP_ONE_LINE, (4, 5), (4, 3), True),
        (MoveType.SKIP_ONE_LINE, (1, 1), (2, 1), False),
    ]


    short_diag_cases = [
        (MoveType.SHORT_DIAG, (1, 1), (2, 2), True),
        (MoveType.SHORT_DIAG, (3, 3), (2, 2), True),
        (MoveType.SHORT_DIAG, (3, 3), (4, 2), True),
        (MoveType.SHORT_DIAG, (2, 4), (3, 3), True),
        (MoveType.SHORT_DIAG, (1, 1), (3, 3), False),
    ]


    long_diag_cases = [
        (MoveType.LONG_DIAG, (1, 1), (3, 3), True),
        (MoveType.LONG_DIAG, (3, 3), (1, 5), True),
        (MoveType.LONG_DIAG, (3, 3), (5, 5), True),
        (MoveType.LONG_DIAG, (3, 4), (1, 2), True),
        (MoveType.LONG_DIAG, (1, 1), (2, 2), False),
    ]

    normal_l_cases = [
        (MoveType.NORMAL_L, (1, 4), (3, 3), True),
        (MoveType.NORMAL_L, (2, 1), (3, 3), True),
        (MoveType.NORMAL_L, (3, 3), (5, 2), True),
        (MoveType.NORMAL_L, (3, 3), (4, 5), True),
        (MoveType.NORMAL_L, (2, 5), (3, 3), False),
    ]

    inversed_l_cases = [
        (MoveType.INVERSED_L, (1, 2), (3, 3), True),
        (MoveType.INVERSED_L, (3, 3), (4, 1), True),
        (MoveType.INVERSED_L, (3, 3), (5, 4), True),
        (MoveType.INVERSED_L, (2, 5), (3, 3), True),
        (MoveType.INVERSED_L, (1, 4), (3, 3), False),
    ]
    skip_three_lines_cases = [
        (MoveType.SKIP_THREE_LINES, (1, 1), (1, 4), True),
        (MoveType.SKIP_THREE_LINES, (2, 2), (2, 6), True),
        (MoveType.SKIP_THREE_LINES, (3, 3), (6, 3), True),
        (MoveType.SKIP_THREE_LINES, (3, 4), (1, 4), True),
        (MoveType.SKIP_THREE_LINES, (2, 2), (2, 5), False),
    ]

    run_test_cases(no_skip_line_cases)
    run_test_cases(skip_one_line_cases)
    run_test_cases(short_diag_cases)
    run_test_cases(long_diag_cases)
    run_test_cases(normal_l_cases)
    run_test_cases(inversed_l_cases)
    run_test_cases(skip_three_lines_cases)


def run_test_cases(cases):
    for type, coords1, coords2, expected in cases:
        assert is_valid_mov(type, coords1, coords2) == expected
