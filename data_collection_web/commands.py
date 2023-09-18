import click

from data_collection_web import app, db
from data_collection_web.models import User, Reaction

@app.cli.command() 
@click.option('--drop', is_flag=True, help='Create after drop.')  
def initdb(drop):
    """Initialize the database."""
    if drop: 
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  
