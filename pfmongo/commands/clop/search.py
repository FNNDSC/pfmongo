import click

@click.command(help="""
                        search collection

""")
@click.option('--document',
              help  = "A JSON formatted file to save to the collection")
def search(document:str):
    print(f"Will add {document}")
