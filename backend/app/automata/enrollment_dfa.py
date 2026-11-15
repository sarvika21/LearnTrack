from enum import Enum

class EnrollmentState(str, Enum):
    NOT_ENROLLED = "NOT_ENROLLED"
    REQUESTED = "REQUESTED"
    ENROLLED = "ENROLLED"
    REJECTED = "REJECTED"

TRANSITIONS = {
    EnrollmentState.NOT_ENROLLED: {"REQUEST": EnrollmentState.REQUESTED},
    EnrollmentState.REQUESTED: {
        "APPROVE": EnrollmentState.ENROLLED,
        "REJECT": EnrollmentState.REJECTED,
        "CANCEL": EnrollmentState.NOT_ENROLLED,
    },
    EnrollmentState.REJECTED: {"REQUEST": EnrollmentState.REQUESTED},
    EnrollmentState.ENROLLED: {"CANCEL": EnrollmentState.NOT_ENROLLED},
}

def transition(state: str, action: str) -> str:
    try:
        current = EnrollmentState(state)
        return TRANSITIONS[current][action.upper()].value
    except (ValueError, KeyError):
        raise ValueError(f"Invalid enrollment transition: {state} --{action}-->")
