
from flask import Blueprint

supplier = Blueprint('supplier', __name__)

from . import routes  # Import routes at the end to avoid circular imports
