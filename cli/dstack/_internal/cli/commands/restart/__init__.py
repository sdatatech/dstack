import os
from argparse import Namespace

from dstack._internal.api.runs import list_runs_hub
from dstack._internal.cli.commands import BasicCommand
from dstack._internal.cli.utils.common import add_project_argument, check_init, console
from dstack._internal.cli.utils.config import config, get_hub_client
from dstack._internal.cli.utils.run import poll_run
from dstack._internal.cli.utils.watcher import Watcher


class RestartCommand(BasicCommand):
    NAME = "restart"
    DESCRIPTION = "Restart run(s)"

    def __init__(self, parser):
        super(RestartCommand, self).__init__(parser)

    def register(self):
        add_project_argument(self._parser)
        self._parser.add_argument("run_name", metavar="RUN", type=str, help="The name of the run")

    @check_init
    def _command(self, args: Namespace):
        hub_client = get_hub_client(project_name=args.project)
        jobs = hub_client.list_jobs(args.run_name)
        if len(jobs) == 0:
            console.print(f"Cannot find the run '{args.run_name}'")
            exit(1)

        console.print("\nRestarting instance...\n")

        for job in jobs:
            hub_client.restart_job(job)

        runs = list_runs_hub(hub_client, run_name=args.run_name)
        run = runs[0]

        # TODO watcher
        poll_run(
            hub_client,
            run,
            jobs,
            ssh_key=config.repo_user_config.ssh_key_path,
            watcher=Watcher(os.getcwd()),
        )
