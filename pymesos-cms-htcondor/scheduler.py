#!/usr/bin/env python2.7
from __future__ import print_function

import sys
import os
import uuid
import time
import socket
import signal
import getpass
from threading import Thread
from os.path import abspath, join, dirname

from pymesos import MesosSchedulerDriver, Scheduler, encode_data
from addict import Dict

TASK_CPU = 0.1
TASK_MEM = 160
EXECUTOR_CPUS = 0.1 
EXECUTOR_MEM = 160


class MinimalScheduler(Scheduler):

    def __init__(self, executor):
        self.executor = executor

    def resourceOffers(self, driver, offers):
        filters = {'refuse_seconds': 5}

        for offer in offers:
            cpus = self.getResource(offer.resources, 'cpus')
            mem = self.getResource(offer.resources, 'mem')
            if cpus < TASK_CPU or mem < TASK_MEM:
                continue

            task = Dict()
            task_id = str(uuid.uuid4())
            task.task_id.value = task_id
            task.agent_id.value = offer.agent_id.value
            task.name = 'task {}'.format(task_id)
            task.executor = self.executor
            task.data = encode_data('Hello from task {}!'.format(task_id))

            task.resources = [
                dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
                dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
            ]

            driver.launchTasks(offer.id, [task], filters)

    def getResource(self, res, name):
        for r in res:
            if r.name == name:
                return r.scalar.value
        return 0.0

    def statusUpdate(self, driver, update):
        logging.debug('Status update TID %s %s',
                      update.task_id.value,
                      update.state)


def main(master):
    executor = Dict()
    executor.executor_id.value = 'MinimalExecutor'
    executor.name = executor.executor_id.value
    executor.command.value = 'python executor.py'
    executor.command.environment.variables = [
        dict(name="FRONTIER_PROXY", value=os.environ["FRONTIER_PROXY"]),
        dict(name="CMS_LOCAL_SITE", value=os.environ["CMS_LOCAL_SITE"]),
        dict(name="PROXY_CACHE", value=os.environ["PROXY_CACHE"])
        ]

    executor.resources = [
        dict(name='mem', type='SCALAR', scalar={'value': EXECUTOR_MEM}),
        dict(name='cpus', type='SCALAR', scalar={'value': EXECUTOR_CPUS}),
        ]

    executor.container.type = "DOCKER"
    executor.container.docker.image = "dodasts/cms:fw"
    executor.container.docker.privileged = True
    executor.container.docker.network = "BRIDGE"
    # force_pull_image=True,
    executor.container.docker.parameters = [
                                        dict(
                                          key="cap-add", 
                                          value="SYS_ADMIN"
                                          )
                                        ]

    executor.container.volumes = [
        dict(
            mode="RO",
            container_path="/sys/fs/cgroup",
            host_path="/sys/fs/cgroup"
            ),
        dict(
            mode="RW",
            container_path="/opt/exp_sw/cms",
            host_path="/opt/exp_sw/cms"
            ),
        dict(
            mode="RW",
            container_path="/cvmfs",
            host_path="/cvmfs"
            ),
        dict(
            mode="RW",
            container_path="/etc/cvmfs/SITECONF",
            host_path="/etc/cvmfs/SITECONF"
            ),
        ]

    framework = Dict()
    framework.user = "root"
    framework.name = "MinimalFramework"
    framework.hostname = socket.gethostname()

    driver = MesosSchedulerDriver(
        MinimalScheduler(executor),
        framework,
        master,
        use_addict=True,
        principal="Mesos-user",
        secret="Mesos-passwd"
    )

    def signal_handler(signal, frame):
        driver.stop()

    def run_driver_thread():
        driver.run()

    driver_thread = Thread(target=run_driver_thread, args=())
    driver_thread.start()

    print('Scheduler running, Ctrl+C to quit.')
    signal.signal(signal.SIGINT, signal_handler)

    while driver_thread.is_alive():
        time.sleep(1)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) != 2:
        print("Usage: {} <mesos_master>".format(sys.argv[0]))
        sys.exit(1)
    else:
        main(sys.argv[1])
