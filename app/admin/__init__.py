
from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import routes  # Import routes at the end to avoid circular imports
