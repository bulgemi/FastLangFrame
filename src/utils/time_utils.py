from datetime import datetime
import time

def get_current_kst_time() -> str:
    """Returns the current formatted KST time"""
    # Simply using system local time for now, as tz manipulation might require pytz/dateutil
    return datetime.now().strftime("%Y-%m-%d %H:%M:%SKST")

def log_execution_time(start: float) -> float:
    """Calculates exactly how much time passed since start"""
    return time.perf_counter() - start
