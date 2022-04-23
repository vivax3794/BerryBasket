import json
import os

from sanic import Sanic, response
from sanic.response import HTTPResponse 
from sanic.request import Request
from sanic_ext import openapi
from loguru import logger

from src.process_manager import ProcessManager

app = Sanic("BerryBasket")
projects: dict[str, ProcessManager] = {}


def start_up():
    for project in os.listdir("projects"):
        with open(f"projects/{project}") as f:
            data = json.load(f)
            project = ProcessManager(data)
            projects[project.name] = project
            logger.info(f"loaded {project.name}")
    
    app.run(debug=True)  # type: ignore


@app.get("/")
@openapi.response(200, dict[str, bool], description="Sucess")
async def root(request: Request) -> HTTPResponse:
    """
    Get projects.

    List projects and wether they are online!  
    """
    return response.json({
        key: value.is_running()
        for key, value in projects.items()
    })

@app.post("/stop/<project_name>")
@openapi.response(400, description="project not running")
@openapi.response(404, description="project not found")
@openapi.response(200, description="project terminated")
@openapi.parameter("project_name", str, "path")
async def stopp_process(request: Request, project_name: str ) -> HTTPResponse:
    if not project_name in projects:
        return response.empty(404)

    project = projects[project_name]
    if project.is_running():
        project.stop_process()
        return response.empty(200)
    else:
        return response.empty(400)

@app.post("/start/<project_name>")
@openapi.response(400, description="project already running")
@openapi.response(404, description="project not found")
@openapi.response(200, description="project started")
@openapi.parameter("project_name", str, "path")
async def start_process(request: Request, project_name: str ) -> HTTPResponse:
    if not project_name in projects:
        return response.empty(404)

    project = projects[project_name]
    if project.is_running():
        return response.empty(400)
    else:
        project.start_process()
        return response.empty(200)

@app.post("/update/<project_name>")
@openapi.response(404, description="project not found")
@openapi.response(200, description="project updated")
@openapi.parameter("project_name", str, "path")
async def start_process(request: Request, project_name: str ) -> HTTPResponse:
    if not project_name in projects:
        return response.empty(404)

    project = projects[project_name]
    project.update_program()
    if project.is_running():
        project.stop_process()
        project.start_process()
    
    return response.empty(200)