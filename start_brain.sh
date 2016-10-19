#!/usr/bin/env bash

cat /dev/null > .brain_job_pids
python -m brain.perception &
echo $! >> .brain_job_pids
python -m brain.action &
echo $! >> .brain_job_pids
