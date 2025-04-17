import pytest
import subprocess
import os
import signal
import time

@pytest.fixture(scope="session", autouse=True)
def start_api():
    proc = subprocess.Popen(
        ["gittxt", "api", "run", "--reload", "--log-level", "error"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    time.sleep(3)
    yield
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
