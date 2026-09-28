from database import init_db, create_api_key, disable_api_key
import typer
from typing import Annotated

app = typer.Typer()


# create the API name in the DB
@app.command("create")
def get_api_name(api_key_name: Annotated[str, typer.Argument()]):
    create_api_key(name=api_key_name)


# disable an API key
@app.command("disable")
def disable_api(id: Annotated[int, typer.Argument()]):
    disable_api_key(id)


if __name__ == "__main__":
    init_db()
    app()


# doctor to check everything

# start llama with the model

# show what's currently running
