"""Tax rates API integration package."""

import os
from typing import Dict, Any
from flask import Blueprint



federal_tax_bp = Blueprint('federal_tax', __name__)
state_tax_bp = Blueprint('state_tax', __name__)


tax_rates_bp = Blueprint('tax_rates', __name__, url_prefix='/api/v1/tax')

from . import routes  # Import routes after blueprint creation to avoid circular imports 