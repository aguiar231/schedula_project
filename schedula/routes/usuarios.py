from http import HTTPStatus
import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from schedula.models import Usuario
from schedula.repositories.usuario import obter_usuario_por_email, obter_usuario_por_id, alterar_usuario
from schedula.security import obter_hash_por_senha, obter_usuario_logado
from schedula.utils import redirecionar_com_toast, processar_imagem_perfil, salvar_imagem_em_arquivo
from jinja2 import Environment

T_UsuarioLogado = Annotated[Usuario, Depends(obter_usuario_logado)]

templates = Jinja2Templates(directory="./schedula/templates")

router = APIRouter(prefix="/usuario", tags=["Usuario"])

def fromjson(value):
    return json.loads(value)

templates.env.filters['fromjson'] = fromjson

@router.get("/perfil", response_class=HTMLResponse)
def mostrar_perfil(
    request: Request,
    usuario: T_UsuarioLogado
): 
    if not usuario:
        return redirecionar_com_toast("/bem-vindo", toast={"mensagem": "Sem acesso!", "tipo": "aviso"})
    

    return templates.TemplateResponse("perfil.html", {"request": request, "titulo": "Perfil :: Schedula", "usuario": usuario})

@router.post("/perfil/alterar")
async def editar_usuario(
    request: Request,
    usuario: T_UsuarioLogado,
    nome: str = Form(None),
    email: str = Form(None),
    telefone: str = Form(None),
    senha: str = Form(None),
    conf_senha: str = Form(None),
    imagem: UploadFile = File(None)
):
    nome = nome if nome != "" else None
    email = email if email != "" else None
    senha = senha if senha != "" else None
    conf_senha = conf_senha if conf_senha != "" else None
    telefone = telefone if telefone != "" else None
    email = email if email != "" else None
    imagem = imagem if imagem.size != 0 else None

    print(imagem)
    if not usuario:
        return redirecionar_com_toast("/bem-vindo", toast={"mensagem": "Sem acesso!", "tipo": "aviso"})
    
    if senha != conf_senha:
        return redirecionar_com_toast("/usuario/perfil", toast={"mensagem": "As senhas não são iguais!", "tipo": "aviso"})
    
    if senha:
        senha = obter_hash_por_senha(senha)
    
    if email:
        _usuario = obter_usuario_por_email(email)
        if _usuario and _usuario.id != usuario.id:
            return redirecionar_com_toast("/usuario/perfil", toast={"mensagem": "Email já cadastrado", "tipo": "aviso"})
        
    if imagem:
        imagem_bytes = await imagem.read() 
        
        imagem_processada = processar_imagem_perfil(imagem_bytes)

        if not imagem_processada:
            return redirecionar_com_toast("/usuario/perfil", toast={"mensagem": "Imagem não é valida!", "tipo": "aviso"})
    
        imagem = salvar_imagem_em_arquivo(imagem_processada, "./schedula/static/bucket/usuario/")
    
    usuario_alterado = Usuario(
        nome=nome,
        email=email,
        senha=senha,
        telefone=telefone,
        imagem=imagem
    )

    usuario = alterar_usuario(
        usuario.id,
        usuario_alterado
    )

    return redirecionar_com_toast("/usuario/perfil", toast={"mensagem": f"Usuário <b>{usuario.nome}</b> atualizado!", "tipo": "aviso"})
    