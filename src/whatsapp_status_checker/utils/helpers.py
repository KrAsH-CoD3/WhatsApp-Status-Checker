"""
Utility functions and helper methods
"""


def calculate_next_reminder_time(ttime_diff: float, sstart: float, reminder_time: int) -> float:
    """Calculate next reminder time based on configured interval"""
    if (
       reminder_time == 1 and ttime_diff >= 1_800  # Every 30 Mins
       or reminder_time == 2 and ttime_diff >= 3_600  # Every 1 Hour
       or reminder_time == 3 and ttime_diff >= 10_800  # Every 3 Hours
       or reminder_time == 4 and ttime_diff >= 21_600  # Every 6 Hours
    ):
        from time import perf_counter
        return float("{:.2f}".format(perf_counter()))
    else:
        return sstart
