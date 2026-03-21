import pytest
import time
from src.utils.time_utils import get_current_kst_time, log_execution_time

def test_get_current_kst_time():
    t = get_current_kst_time()
    assert "KST" in t
    
def test_log_execution_time():
    start = time.perf_counter()
    time.sleep(0.01)
    duration = log_execution_time(start)
    assert duration > 0.0
