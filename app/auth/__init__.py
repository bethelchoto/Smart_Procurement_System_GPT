
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes  # Import routes at the end to avoid circular imports
