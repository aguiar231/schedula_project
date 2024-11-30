from http import HTTPStatus
import json
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from schedula.models import Usuario
from schedula.repositories.usuario import inserir_usuario, obter_usuario_por_email, alterar_token_por_id
from schedula.utils import redirecionar_com_toast
from schedula.security import obter_hash_por_senha, verificar_senha, gerar_token, obter_usuario_logado, criar_cookie_token, deletar_cookie_token
from jinja2 import Environment

templates = Jinja2Templates(directory="./schedula/templates")

router = APIRouter(tags=["Root"])
T_UsuarioLogado = Annotated[Usuario, Depends(obter_usuario_logado)]

def fromjson(value):
    return json.loads(value)

templates.env.filters['fromjson'] = fromjson


@router.get("/")
def root_bem_vindo():

    return RedirectResponse("/bem-vindo", 303)

@router.get("/bem-vindo", status_code=HTTPStatus.OK, response_class=HTMLResponse)
def root_bem_vindo(
    request: Request,
    usuario: T_UsuarioLogado
):
    return templates.TemplateResponse("bem_vindo.html", {"request": request, "usuario": usuario, "titulo": "Home :: Contato"})

@router.get("/contato", status_code=HTTPStatus.OK, response_class=HTMLResponse)
def root_contato(request: Request, usuario: T_UsuarioLogado):

    return templates.TemplateResponse("contato.html", {"request": request, "usuario": usuario, "titulo": "Schedula :: Contato"})

@router.get("/login", status_code=HTTPStatus.OK, response_class=HTMLResponse)
def root_login(request: Request, usuario: T_UsuarioLogado):

    return templates.TemplateResponse("login.html", {"request": request, "usuario": usuario, "titulo": "Schedula :: Login"})

@router.get("/registrar", status_code=HTTPStatus.OK, response_class=HTMLResponse)
def root_register(request: Request, usuario: T_UsuarioLogado):

    return templates.TemplateResponse("registrar.html", {"request": request, "usuario": usuario, "titulo": "Schedula :: Registrar"})
  
@router.get("/sobre", status_code=HTTPStatus.OK, response_class=HTMLResponse)
def root_login(request: Request, usuario: T_UsuarioLogado):

    return templates.TemplateResponse("sobre.html", {"request": request, "usuario": usuario, "titulo": "Schedula :: Sobre"})

@router.post("/login", status_code=HTTPStatus.OK)
def root_login(email: str = Form(), senha: str = Form()):
    usuario = obter_usuario_por_email(email)

    if not usuario:
        return redirecionar_com_toast("/login", toast={"mensagem": "Email ou senha Incorretos!", "tipo": "aviso"})
    
    if not verificar_senha(senha_simples=senha, senha_hashed=usuario.senha):
        return redirecionar_com_toast("/login", toast={"mensagem": "Email ou senha Incorretos!", "tipo": "aviso"})
    
    token = gerar_token()
    alterar_token_por_id(id=usuario.id, token=token)
    response = redirecionar_com_toast("/", toast={"mensagem": f"<b>{usuario.nome}</b>\n Bem vindo de volta!", "tipo": "bom"})
    criar_cookie_token(response, token)
    return response

@router.post("/registrar", status_code=HTTPStatus.OK, response_class=RedirectResponse)
def root_register(
    nome: str = Form(),
    email: str = Form(),
    senha: str = Form(),
    conf_senha: str = Form()
):
    if senha != conf_senha:
        return redirecionar_com_toast("/registrar", toast={"mensagem": "As senhas não são iguais!", "tipo": "aviso"})
    
    if obter_usuario_por_email(email):
        return redirecionar_com_toast("/registrar", toast={"mensagem": "Email já cadastrado", "tipo": "aviso"})

    senha_hashed = obter_hash_por_senha(senha)
    
    usuario = inserir_usuario(
        usuario=Usuario(
            nome=nome,
            email=email,
            senha=senha_hashed,
            administrador=0
        )
    )

    token = gerar_token()
    alterar_token_por_id(id=usuario.id, token=token)

    response = redirecionar_com_toast("/", toast={"mensagem": f"<b>{usuario.nome}</b> conta criada com sucesso!", "tipo": "bom"})
    criar_cookie_token(response, token)
    return response

@router.get("/logout", status_code=HTTPStatus.OK, response_class=RedirectResponse)
def root_logout(usuario: T_UsuarioLogado):
    if not usuario:
        return redirecionar_com_toast("/", toast={"mensagem": "Sem acesso!", "tipo": "aviso"})
    
    alterar_token_por_id(usuario.id, "")
    response = redirecionar_com_toast("/", toast={"mensagem": f"Até logo <b>{usuario.nome}</b>", "tipo": "bom"})
    response = deletar_cookie_token(response)

    return response