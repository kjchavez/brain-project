#!/usr/bin/env bash

while read p; do
      kill $p
done <.brain_job_pids
