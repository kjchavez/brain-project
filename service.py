#! /usr/bin/env python

import subprocess
import os
import argparse
import yaml

RUNTIME_DATA_DIR=".brain_runtime"
SERVICE_PIDS_FILE = os.path.join(RUNTIME_DATA_DIR, ".service_pids")

def load_pids():
    if not os.path.isdir(RUNTIME_DATA_DIR):
        os.makedirs(RUNTIME_DATA_DIR)

    if os.path.exists(SERVICE_PIDS_FILE):
        with open(SERVICE_PIDS_FILE, 'r') as fp:
            pids = yaml.load(fp)
    else:
        pids = {}

    return pids

def stop_service(name):
    pids = load_pids()
    pid = pids.get(name)
    if not pid:
        print "Service not found."
    else:
        print "Bringing down %s with PID %s." % (name, pid)
        subprocess.Popen(['kill', '-9', str(pid)]).wait()

def start_service(name, loglevel="info", config=None):
    pids = load_pids()
    module_name = "brain.services.%s.run" % name
    flags = []
    flags.extend(["--loglevel", loglevel])

    if config:
        flags.extend(["--config", config])

    print "Starting up %s module." %name
    cmd = ['python', '-m', module_name] + flags
    popen = subprocess.Popen(cmd)

    # Update pids
    pids[name] = popen.pid

    with open(SERVICE_PIDS_FILE, 'w') as fp:
        yaml.dump(pids, fp, default_flow_style=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["start", "stop"])
    parser.add_argument("module")
    parser.add_argument("--config", default=None)
    parser.add_argument("--loglevel",
            choices=["debug", "info", "warning", "error"], default="info")

    args = parser.parse_args()

    if args.operation == "stop":
        stop_service(args.module)
    elif args.operation == "start":
        start_service(args.module, loglevel=args.loglevel,
                      config=args.config)

if __name__ == "__main__":
    main()
