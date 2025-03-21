# app/cli.py

import click
from flask.cli import with_appcontext
from app.api.tax_rates.models import StateInfo, StateTaxBracket
from app import create_app, db



@click.command('populate-state-data')
@with_appcontext
def populate_state_data_command():
    """Populate the database with state tax data."""
    from scripts.populate_state_data import populate_state_info, populate_tax_brackets

    click.echo('Populating state information...')
    populate_state_info()
    click.echo('Populating tax brackets...')
    populate_tax_brackets()
    click.echo('Database population completed!')


# Then in app/__init__.py, add:

def register_cli_commands(app):
    from .cli import populate_state_data_command
    app.cli.add_command(populate_state_data_command)


# In your create_app function, add:
def create_app(config_name):
    app = Flask(__name__)
    # ... other initialization code ...

    register_cli_commands(app)
    return app
