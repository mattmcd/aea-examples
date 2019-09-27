#!/usr/bin/env python3
from __future__ import print_function
import json
import subprocess
import argparse
import sys
import os


def run(cmd):
    print(' '.join(cmd))
    c = subprocess.Popen(cmd)
    c.wait()
    return c.returncode


def error(*x):
    print(''.join([str(xx) for xx in x]), file=sys.stderr)


def fail(*x):
    error(x)
    exit(1)


def pull_image(run_sudo, img):
    c = []

    if run_sudo:
        c += [ 'sudo' ]
    c += [
        'docker',
        'pull',
        img,
    ]
    r = run(c)
    if r != 0:
        error("can't pull " + img)


def parse_command(j):
    cmd = []
    used_keys = ["positional_args"]
    for key in j["positional_args"]:
        cmd.append(str(j[key]))
        used_keys.append(key)
    for key in j:
        if key in used_keys:
            continue
        cmd.extend(
            [
                "--"+key,
                str(j[key])
            ]
        )
    return cmd


def launch_job(args, j):
    img = j['image']
    if '/' in img:
        pull_image(args.sudo, img)

    c = []
    if args.sudo:
        c += ['sudo']
    c += [
        'docker',
        'run'
    ]
    if args.background:
        c += ['-d']
    else:
        c += ['-it']
    work_dir = os.path.abspath(os.path.dirname(__file__))
    project_dir = os.path.abspath(os.path.join(work_dir, '..', '..'))
    print("Work dir: ", work_dir)
    c += [
        "-v",
        work_dir+":/config",
        "-v",
        project_dir+"/data/oef-logs:/logs"
    ]

    for arg in j['params']:
        c += map(lambda x: x.replace("$PWD", project_dir), arg)

    c += [img]

    cmd_config = j["cmd"].get(args.cmd, None)
    if not cmd_config:
        fail("Selected command {} not configured in config file!".format(args.cmd))

    c.extend(parse_command(cmd_config))
    extra_args = [a for a in args.rest if a != "--"]
    print("Extra arguments to search: ", extra_args)
    c += extra_args
    r = run(c)
    if r != 0:
        fail("can't launch " + img)


def main(args):
    with open(args.config, "r") as f:
        config = json.load(f)
    launch_job(args, config)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True, type=str, help='Publish the image to GCR')
    parser.add_argument("--sudo", required=False, action='store_true', help="Run docker as root")
    parser.add_argument("--background", required=False,  action='store_true', help="Run image in background.")
    parser.add_argument("--cmd", required=False, type=str, default="oef-search", help="The available commands are defined"
                                                                                    " in the config file "
                                                                                    "('cmd' dictionary) ")
    parser.add_argument('rest', nargs=argparse.REMAINDER)
    main(parser.parse_args())