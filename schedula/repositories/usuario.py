from typing import List
from schedula.utils import obter_conexao
from schedula.models import Usuario

from schedula.sql.usuario_sql import *

def inserir_usuario(usuario: Usuario) -> Usuario | None:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db.execute(SQL_INSERIR,
            (
                usuario.nome,
                usuario.email,
                usuario.senha,
                usuario.administrador
            )    
        )
        if db.rowcount <= 0:
            return None
        
        usuario.id = db.lastrowid
        return usuario
    
def obter_todos_usuarios() -> List[Usuario]:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_usuarios = db.execute(SQL_OBTER_TODOS).fetchall()

        usuarios = [Usuario(*db_usuario) for db_usuario in db_usuarios]
        return usuarios
    
def obter_usuario_por_id(id: int) -> Usuario | None:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_usuario = db.execute(SQL_OBTER_POR_ID, (id,)).fetchone()
        print(db_usuario)
        
        if not db_usuario:
            return None
        
        usuario = Usuario(*db_usuario)
        return usuario
    
def obter_usuario_por_email(email: str) -> Usuario | None:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_usuario = db.execute(SQL_OBTER_USUARIO_POR_EMAIL, (email,)).fetchone()
        
        if not db_usuario:
            return None
        
        usuario = Usuario(*db_usuario)
        return usuario
        
def obter_usuario_por_token(token: str) -> Usuario | None:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_usuario = db.execute(SQL_OBTER_POR_TOKEN, (token,)).fetchone()

        if not db_usuario:
            return None
        
        usuario = Usuario(*db_usuario)
        print(usuario)
        return usuario

def alterar_token_por_id(id: int, token: str) -> Usuario | None:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_usuario = db.execute(SQL_ALTERAR_TOKEN, (token, id)).fetchone()

        if not db_usuario:
            return None
        
        usuario = Usuario(*db_usuario)
        return usuario

def alterar_usuario(id: int, usuario: Usuario) -> Usuario | None:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db.execute(SQL_ALTERAR,
            (
                usuario.nome,
                usuario.email,
                usuario.telefone,
                usuario.senha,
                usuario.imagem,
                id
            )    
        )
        conexao.commit()
        if db.rowcount <= 0:
            return None
        
        usuario.id = db.lastrowid
        return usuario