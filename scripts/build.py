#!/usr/bin/env python

import sys
import subprocess as sp

import os
from contextlib import contextmanager

eprint = lambda *args, **kwargs: print('[DEPLOY]', *args, **kwargs)
debug = lambda *args, **kwargs: eprint('[DEBUG]', *args, **kwargs)
error = lambda *args, **kwargs: eprint('[ERROR]', *args, **kwargs)

# Path from the remote repository to the directory containing the branches.
BRANCHES_DIR = '..'

is_deploy_setup = lambda branch: os.path.exists(os.path.join(BRANCHES_DIR, branch))

class Checkout:
    def __init__(self, branch_name):
        self._branch_name = branch_name

    def to(self, deploy_dir):
        self._deploy_dir = deploy_dir
        return self

    def run(self):
        return sp.call(
                [
                    'git',
                    '--work-tree',
                    deploy_dir,
                    'checkout',
                    '-f',
                    branch_name,
                ],
        )

    __call__ = run

class LockError(RuntimeError):
    pass

@contextmanager
def lock_file(f):
    try:
        with open(f, 'rt') as h:
            l = h.readline().rstrip()
            raise LockError('Deployment directory is locked by process', l)
    except IOError:
        pass

    try:
        with open(f, 'wt') as h:
            print(os.getpid(), file=h)
    except IOError:
        raise LockError('Deployment directory was locked by another process',
                'in a race condition.',
        )

    try:
        yield
    finally:
        os.remove(f)

@contextmanager
def chdir(path):
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)

if __name__ == '__main__':
    ref_name, old_value, new_value = sys.argv[1:4]

    # the ref_name has the format 'refs/heads/BRANCH'
    branch_name = ref_name.split('/', 3)[-1]
    deploy_dir = os.path.join('..', branch_name)

    # Check that PTD is set up for that branch.
    if not is_deploy_setup(branch_name):
        error("push-to-deploy not set up for branch", branch_name)
        sys.exit(1)

    try:
        with lock_file(deploy_dir + '.lock'):
            # Checkout the updated code to the deploy directory
            return_code = Checkout(branch_name).to(deploy_dir).run()

            if return_code == 0:
                eprint('checkout', branch_name, '->', new_value)
            else:
                error('checkout FAILED', branch_name, '->', new_value)
                sys.exit(1)

            with chdir(deploy_dir):
                return_code = sp.call(['make'])

            if return_code == 0:
                eprint('webapp build succeeded.')
            else:
                error('webapp build FAILED.')
                sys.exit(1)

            return_code = sp.call(
                    [
                        'sudo',
                        'systemctl',
                        'restart',
                        'ahvoda-' + branch_name,
                    ],
            )

            if return_code == 0:
                eprint('restarted gunicorn daemon for', branch_name)
            else:
                eprint('restarting gunicorn daemon FAILED for',
                        branch_name, '- does the systemd unit exist?',
                )
                sys.exit(1)

            return_code = sp.call(
                    [
                        'sudo',
                        'systemctl',
                        'status',
                        'ahvoda-' + branch_name,
                    ],
            )
    except LockError as e:
        error('failed to lock the deployment directory',
                deploy_dir + ':', e,
        )
        sys.exit(1)
