from signal import SIGINT
import subprocess
import os
from typing import TypedDict

from loguru import logger
import psutil


class ProcessData(TypedDict):
    name: str
    folder: str
    git_url: str
    command: list[str]
    autostart: bool
    restart_on_failure: bool


class ProcessManager:
    def __init__(self, data: ProcessData) -> None:
        self.name = data["name"]
        self.folder = data["folder"]
        self.command = data["command"]
        self.autostart = data["autostart"]
        self.restart_on_failure = data["restart_on_failure"]

        self.process: subprocess.Popen[bytes] | None = None

        if self.autostart:
            self.update_program()
            self.start_process()
    
    def start_process(self) -> None:
        if self.process is not None:
            raise RuntimeError("Process is already running")
        
        self.process = subprocess.Popen(
            self.command,
            env={"PATH": os.environ["PATH"]},
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            cwd=self.folder,
            shell=True
        )

        logger.info(f"started {self.name}")

    def stop_process(self) -> None:
        if self.process is None:
            raise RuntimeError("Process is not running")
        
        parent = psutil.Process(self.process.pid)
        for child in parent.children(recursive=True):
            child.terminate()
        parent.terminate()
        self.process = None
        logger.info(f"stopped {self.name}")
    
    def update_program(self) -> None:
        subprocess.run(["git", "pull"], cwd=self.folder)
        logger.info(f"updaded {self.name}")

    def is_running(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None