import sqlite3
from time import sleep

from schedula.utils import obter_conexao

from schedula.security import obter_hash_por_senha

from schedula.sql import db_create_tables, db_drop_tables, db_triggers, db_default_sql

from schedula.models import Usuario


def create_tables():
    print("Iniciando a criação de tabelas do banco!")
    sleep(2)
    try:
        with obter_conexao() as conexao:
            db = conexao.cursor()
            db.executescript(db_create_tables.SQL_CREATE_TABLES)
            print("Tabelas Criadas!")
            sleep(2)
            db.executescript(db_triggers.SQL_CRIAR_TRIGGERS)
            print("Triggers Criados!")
            conexao.commit()
    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao criar as tabelas: {e}")
    sleep(2)
    print("Operação Finalizada!")
    
def drop_tables():
    while True:
        res = input("Você realmente desejar apagar as tabelas e dados do banco de dados ?\n1 - Sim | 2 - Não\n")
        sleep(2)
        if res.isdigit():
            res = int(res)
            if res == 1:
                try:
                    with obter_conexao() as conexao:
                        db = conexao.cursor()
                        db.executescript(db_drop_tables.SQL_DROP_TABLES)
                        conexao.commit()
                        print("Tabelas Deletadas!")
                        sleep(2)
                        print("Operação Finalizada!")
                except sqlite3.Error as e:
                    print(f"Ocorreu um erro ao deletar as tabelas: {e}")
                    break
                break
            elif res == 2:
                sleep(2)
                print("Operação Finalizada!") 
                break
            else:
                print("Opção Inválida...")
                sleep(2)
        else:
            print("Opção Inválida")
            sleep(2)

def insert_user_adm_default():
    try:
        with obter_conexao() as conexao:
                db = conexao.cursor()
                db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuario'")
                tabela_existe = db.fetchone()
                if not tabela_existe:
                    print("A tabela 'usuario' não existe. Não será possível criar o usuário administrador.")
                    return
    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao verificar se a tabela usuarios existe: {e}")

    print("Registro da conta Administrador")
    name = input("nome: ")
    email = input("email: ")
    pw = input("senha: ")
    pw = obter_hash_por_senha(pw)
    user = Usuario(nome=name, email=email, senha=pw)
    
    try:
        with obter_conexao() as conexao:
            db = conexao.cursor()
            db.execute(db_default_sql.SQL_CRIAR_USER_ADMINISTRADOR_DEFAULT, (user.nome, user.email, user.senha, 1))
            conexao.commit()
            print("Usuario Administrador Criado!")
            sleep(2)
            
    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao deletar as tabelas: {e}")

def init():
    ...