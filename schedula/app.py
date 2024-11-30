from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


from schedula.routes import usuarios, root, sala

app = FastAPI()

app.mount(path="/static", app=StaticFiles(directory="./schedula/static"), name="static")


app.include_router(usuarios.router)
app.include_router(sala.router)
app.include_router(root.router)
