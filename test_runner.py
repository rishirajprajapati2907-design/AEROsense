import subprocess
import sys

cmd = [sys.executable, "-m", "pytest", "tests/test_api_auth_team.py", "tests/test_api_domain_routers.py", "tests/test_scheduler.py", "tests/test_frontend_serving.py", "tests/test_components_deprecation.py", "-v"]
res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:\n", res.stdout[-1500:])
if res.stderr:
    print("STDERR:\n", res.stderr[-500:])
print("Return code:", res.returncode)
