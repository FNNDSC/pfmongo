import click

@click.command(help="""
                        show collection

""")
@click.option('--document',
              help  = "A JSON formatted file to save to the collection")
def show(document:str):
    print(f"Will add {document}")
