from enum import Enum

class LessonState(str, Enum):
    LOCKED = "LOCKED"
    UNLOCKED = "UNLOCKED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    QUIZ_PASSED = "QUIZ_PASSED"

TRANSITIONS = {
    LessonState.LOCKED: {"UNLOCK": LessonState.UNLOCKED},
    LessonState.UNLOCKED: {"START": LessonState.IN_PROGRESS},
    LessonState.IN_PROGRESS: {"COMPLETE": LessonState.COMPLETED},
    LessonState.COMPLETED: {"PASS_QUIZ": LessonState.QUIZ_PASSED},
    LessonState.QUIZ_PASSED: {},
}

def transition(state: str, action: str) -> str:
    try:
        current = LessonState(state)
        return TRANSITIONS[current][action.upper()].value
    except (ValueError, KeyError):
        raise ValueError(f"Invalid lesson transition: {state} --{action}-->")
