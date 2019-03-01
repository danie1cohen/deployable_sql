from . import frequency_types
from . import frequency_intervals
from . import job_step_actions


FREQUENCY_TYPES = {
    'once': frequency_types.ONCE,
    'daily': frequency_types.DAILY,
    'weekly': frequency_types.WEEKLY,
    'monthly': frequency_types.MONTHLY,
    'monthly_relative': frequency_types.MONTHLY_RELATIVE,
    'on_agent_start': frequency_types.ON_AGENT_START,
    'idle': frequency_types.IDLE,
}

FREQUENCY_INTERVALS = {
    'sunday': frequency_intervals.SUNDAY,
    'monday': frequency_intervals.MONDAY,
    'tuesday': frequency_intervals.TUESDAY,
    'wednesday': frequency_intervals.WEDNESDAY,
    'thursday': frequency_intervals.THURSDAY,
    'friday': frequency_intervals.FRIDAY,
    'saturday': frequency_intervals.SATURDAY,
}

JOB_STEP_ACTIONS = {
    'quit_with_success': job_step_actions.QUIT_WITH_SUCCESS,
    'quit_with_failure': job_step_actions.QUIT_WITH_FAILURE,
    'go_to_next_step': job_step_actions.GO_TO_NEXT_STEP,
    'go_to_step_id': job_step_actions.GO_TO_STEP_ID,
}
