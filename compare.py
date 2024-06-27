# directory setup:

# $ python -m venv venv1
# $ python -m venv venv2
# $ venv1/bin/pip install git+https://github.com/python/mypy.git
# $ venv2/bin/pip install git+https://github.com/A5rocks/mypy.git@[whatever]
# such as:
# $ venv2/bin/pip install git+https://github.com/python/mypy.git@refs/pull/[whatever]/head

# for mypyc, just have these env variables: CC=clang MYPYC_OPT_LEVEL=2 MYPY_USE_MYPYC=1

import pathlib
import json
import subprocess
import tempfile
import multiprocessing
import difflib
import sys
import re

here = pathlib.Path(".") / "issues"

def process(codes_file):
  # print(f"executing mypy on {codes_file}")
  with open(codes_file) as f:
    codes = json.loads(f.read())

  for code in codes:
    with tempfile.NamedTemporaryFile("w", delete_on_close=False) as f:
      f.write(code)
      f.close()
      try:
        run1 = subprocess.run(["venv1/bin/mypy", f.name, "--no-incremental"], capture_output=True, text=True, timeout=30)
        run2 = subprocess.run(["venv2/bin/mypy", f.name, "--no-incremental"], capture_output=True, text=True, timeout=30)
      except subprocess.TimeoutExpired:
        print(f"hit timeout on {codes_file}")
        break

      normalized1 = run1.stdout
      normalized2 = run2.stdout.replace("venv2", "venv1")

      normalized1 = re.sub("`\\d+", "`<id>", normalized1)
      normalized2 = re.sub("`\\d+", "`<id>", normalized2)

      if run1.stderr != "" or run2.stderr != "":
        # print(f"!!!! stderr is not empty: {codes_file}")
        # TODO: compare crashes? maybe? IDK....
        pass
      if normalized1 != normalized2:
        print(f"------- difference on {codes_file}")
        diff = difflib.Differ().compare(normalized1.splitlines(keepends=True), normalized2.splitlines(keepends=True))
        print("".join(diff))
        print("-------")

if __name__ == "__main__":
  # save 1 core unless this is on GHA
  min_cores = min(multiprocessing.cpu_count(), 4)
  with multiprocessing.Pool(max(multiprocessing.cpu_count() - 1, min_cores)) as pool:
    pool.map(process, here.glob("**/blocks.json"))
