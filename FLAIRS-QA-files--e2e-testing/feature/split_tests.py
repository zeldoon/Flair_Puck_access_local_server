#!/usr/bin/env python

import os
from glob import glob
from functools import reduce

MAX_AGENTS = 8
if "MAX_AGENTS" in os.environ.keys():
    MAX_AGENTS = int(os.environ["MAX_AGENTS"])

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

tests = [
    "/".join(test.split("/")[-3:]) for test in glob(f"{SCRIPT_DIR}/tests/test*.py")
]
tests.sort(key=lambda f: os.path.getsize(f), reverse=True)
total_test_size = reduce(
    lambda x, y: x + os.path.getsize(y), tests, os.path.getsize(tests[0])
)

splits = []
for test in tests:
    testname = test[:-3]
    testname = testname.split("__")[0]
    testname = "_".join(testname.split("_")[1:])
    if len(splits) < MAX_AGENTS:
        splits.append({"name": testname, "size": os.path.getsize(test), "list": [test]})
        continue
    for split in splits:
        if split["size"] > (total_test_size // MAX_AGENTS):
            continue
        split["name"] = "_and_".join([split["name"], testname])
        split["list"].append(test)
        split["size"] += os.path.getsize(test)
        break

written_splits = []
for i, split in enumerate(splits):
    split_filename = f'split_{i}_{split["name"]}_{i}.txt'
    with open(f"{SCRIPT_DIR}/{split_filename}", "w") as ofh:
        ofh.write("\n".join(split["list"]))
        ofh.write("\n")
    written_splits.append(f"'feature/{split_filename}'")


with open(f"{SCRIPT_DIR}/Jenkinsfile") as fh:
    jflines = fh.read().split("\n")

values_value = ", ".join(written_splits)
flag_comment = [s for s in jflines if "// REPLACE FOLLOWING" in s][0]
values_comment_index = jflines.index(flag_comment) + 1
values_spaces = jflines[values_comment_index].split("v")[0]
values_line = f"{values_spaces}values {values_value}"
jflines[values_comment_index] = values_line
# del(jflines[values_comment_index - 1])

with open(f"{SCRIPT_DIR}/Jenkinsfile", "w") as wfh:
    wfh.write("\n".join(jflines))
