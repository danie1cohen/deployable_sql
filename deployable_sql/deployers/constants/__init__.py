from . import frequency_types
from . import frequency_intervals


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
