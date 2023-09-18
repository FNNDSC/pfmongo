from re import search
import click

@click.command(help="""
                        delete from collection

""")
@click.option('--document',
              help  = "A JSON formatted file to save to the collection")
def delete(document:str):
    print(f"Will add {document}")
