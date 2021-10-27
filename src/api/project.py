from flask import Blueprint, g, request
from src.services import teams_service as service
from src.models.team import Team

api = Blueprint('projects_api', __name__)

#when adding roles: make sure that the creator has access and permissions to add team to the workspace
# @projects_api.route("/team", methods=['POST'])
# def create_project():