from flask import Blueprint

bp = Blueprint(__name__, __name__)

from . import data
