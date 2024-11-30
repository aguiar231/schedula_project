import datetime
from typing import List
from schedula.utils import obter_conexao
from schedula.models import ReservaSala, Sala, TipoSala, DisponibilidadeSemanalSala

from schedula.sql.sala_sql import *


def inserir_sala(sala: Sala) -> Sala | None:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db.execute(
            SQL_INSERIR_SALA,
            (
                sala.nome,
                sala.capacidade,
                sala.bloco,
                sala.andar,
                sala.numero_sala,
                sala.tipo_sala,
                sala.observacoes,
                sala.imagem,
                sala.status,
                sala.intervalo_tempo
            )
        )
        if db.rowcount < 0:
            return None
        
        sala.id = db.lastrowid
        return sala
    
def inserir_disponibilidade_semanal_padrao(sala_id: int):
    dias_da_semana = [
        'SEGUNDA', 'TERÇA', 'QUARTA', 'QUINTA', 'SEXTA', 'SÁBADO', 'DOMINGO'
    ]
    horarios = ('08:00', '18:00')
    ativo = 0  

    with obter_conexao() as conexao:
        db = conexao.cursor()
        for dia in dias_da_semana:
            db.execute(
                SQL_INSERIR_DISPONIBILIDADE_SEMANAL_PADRAO,
                (sala_id, dia, horarios[0], horarios[1], ativo)
            )
        conexao.commit()
    return None
    
def obter_todas_salas() -> List[Sala]:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_salas = db.execute(SQL_OBTER_TODAS_SALAS).fetchall()
        salas = [Sala(*db_sala) for db_sala in db_salas]
        return salas
     
def obter_sala_por_id(id: int) -> Sala | None:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_sala = db.execute(SQL_OBTER_POR_ID_SALA, (id,)).fetchone()
        
        if not db_sala:
            return None
        
        sala = Sala(*db_sala)
        return sala
        
def obter_tipos_salas() -> TipoSala | None:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_tipos = db.execute(SQL_OBTER_TODOS_TIPO_SALA).fetchall()
        tipos_sala = [Sala(*db_tipo) for db_tipo in db_tipos]
        return tipos_sala
    
def obter_salas_filtro_nome(filter_nome: str) -> List[Sala] | None:
    with obter_conexao() as conexao:
        termo = f"%{filter_nome}%"
        db = conexao.cursor()
        db_salas = db.execute(SQL_FILTRAR_SALAS_PELO_NOME, (termo,)).fetchall()
        salas = [Sala(*db_sala) for db_sala in db_salas]
        return salas
    
def obter_dias_semanas_disponivel_pelo_id(id: int) -> List[DisponibilidadeSemanalSala]:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_dias = db.execute(SQL_OBTER_DISPONIBILIDADE_SEMANAL_PELO_SALA_ID, (id,)).fetchall()
        dias_disponiveis = [DisponibilidadeSemanalSala(*db_dia) for db_dia in db_dias]
        return dias_disponiveis
    
def obter_reservas_por_usuario(usuario_id: int) -> List[ReservaSala]:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_reservas = db.execute(SQL_OBTER_RESERVAS_PELO_USUARIO_ID, (usuario_id,)).fetchall()
        reservas = [ReservaSala(*db_reserva) for db_reserva in db_reservas]
        return reservas

def obter_todas_reservas_por_status() -> List[ReservaSala]:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_reservas = db.execute(SQL_OBTER_RESERVAS).fetchall()
        reservas = [ReservaSala(*db_reserva) for db_reserva in db_reservas]
        return reservas

def inserir_reserva_sala(reserva: ReservaSala) -> ReservaSala | None:
    with obter_conexao() as conexao:
        data_reserva = reserva.data_reserva.isoformat()  # "YYYY-MM-DD"
        horario_inicio = reserva.horario_inicio.isoformat()  # "HH:MM:SS"
        horario_fim = reserva.horario_fim.isoformat() # "HH:MM:SS"
        db = conexao.cursor()
        db.execute(
            SQL_INSERIR_RESERVA_SALA,
            (
                reserva.usuario_id,
                reserva.sala_id,
                data_reserva,
                horario_inicio,
                horario_fim,
                reserva.status
            ),
        )
        if db.rowcount < 0:
            return None
        
        reserva.id = db.lastrowid
        return reserva
    
def verificar_conflito_reserva(reserva: ReservaSala) -> ReservaSala | None:
    print(reserva)
    with obter_conexao() as conexao:
        data_reserva = reserva.data_reserva.isoformat()  # "YYYY-MM-DD"
        horario_inicio = reserva.horario_inicio.isoformat()  # "HH:MM:SS"
        horario_fim = reserva.horario_fim.isoformat() # "HH:MM:SS"
        db = conexao.cursor()
        db.execute(
            SQL_VERIFICAR_CONFLITOS_RESERVA,
            (
                reserva.sala_id,
                data_reserva,
                horario_inicio,
                horario_fim,
                horario_inicio,
                horario_fim,
                horario_inicio,
                horario_fim,
            ),
        )
       
        if len(db.fetchall()) > 0:
            return True
        
        return False
    
def alterar_status_reserva_confirmada(status, reserva_id: int) -> bool:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_reserva = db.execute(SQL_ALTERAR_STATUS_RESERVA, (status, reserva_id)).fetchone()
        conexao.commit()
        
        if not db_reserva:
            return None
        
        reserva = ReservaSala(*db_reserva)
        return reserva
    
def obter_reservas_por_usuario_paginado_com_filtro(usuario_id: int, pagina: int, data_reserva: str, status: str, itens_por_pagina: int = 10):
    offset = (pagina - 1) * itens_por_pagina  # Calcula o deslocamento com base na página atual
    query = SQL_OBTER_RESERVAS_PAGINADO_PELO_USUARIO_ID
    params=[usuario_id]

    if data_reserva:
        query += " AND data_reserva = ?"
        params.append(data_reserva)
    if status:
        query += " AND status = ?"
        params.append(status)

    query += " LIMIT ? OFFSET ?"
    params.extend([itens_por_pagina, offset])

    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_reservas = db.execute(query, params).fetchall()
        reservas = [ReservaSala(*db_reserva) for db_reserva in db_reservas]
    return reservas

def obter_contagem_reservas_por_usuario_com_filtro(usuario_id: int, data_reserva=None, status=None):
    query = SQL_CONTAR_RESERVAS
    params = [usuario_id]
    
    if data_reserva:
        query += " AND data_reserva = ?"
        params.append(data_reserva)

    if status:
        query += " AND status = ?"
        params.append(status)
        
    with obter_conexao() as conexao:
        db = conexao.cursor()
        total = db.execute(query, params).fetchone()
    return total[0]

def obter_contagem_salas_com_filtro(status=None, tipo_sala=None):
    query = SQL_CONTAR_SALAS
    params = []

    if tipo_sala:
        query += " AND tipo_sala = ?"
        params.append(tipo_sala)

    if status:
        query += " AND status = ?"
        params.append(status)


    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_salas = db.execute(query, params).fetchone()

    return db_salas[0]

def obter_salas_paginado_com_filtro(status: str, tipo_sala: int, pagina: int, itens_por_pagina: int = 10):
    offset = (pagina - 1) * itens_por_pagina 
    query = SQL_OBTER_SALAS_PAGINADA
    params = []

    if tipo_sala:
        query += " AND tipo_sala = ?"
        params.append(tipo_sala)

    if status:
        query += " AND status = ?"
        params.append(status)

    query += " LIMIT ? OFFSET ?"
    params.extend([itens_por_pagina, offset])

    with obter_conexao() as conexao:
        db = conexao.cursor()
        db_salas = db.execute(query, params).fetchall()
        salas = [Sala(*db_sala) for db_sala in db_salas]

    return salas

def deletar_sala_por_id(sala_id: int):
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db.execute(SQL_DELETAR_SALA_POR_ID, (sala_id,)).fetchone()
        conexao.commit()
    
        return db.rowcount > 0

def deletar_reservas_por_sala_id(sala_id: int):
    with obter_conexao() as conexao:
        db = conexao.cursor()

        # Obter o número de reservas associadas à sala
        reservas = db.execute(SQL_CONTAR_RESERVAS_POR_SALA, (sala_id,)).fetchone()
        if reservas and reservas[0] > 0:  # Verifica se há reservas
            # Deletar todas as reservas associadas à sala
            db.execute(SQL_DELETAR_TODAS_RESERVAS_PELA_SALA, (sala_id,))
            conexao.commit()
            return True

        # Retorna True caso não haja reservas para a sala
        return True
    
def deletar_disponibilidades_semanal_por_sala_id(sala_id: int):
    with obter_conexao() as conexao:
        db = conexao.cursor()
        disponibilidas =  db.execute(SQL_CONTAR_DISPONIBILIDADE_SEMANAL_PELO_SALA_ID_POR_SALA, (sala_id,)).fetchone()
        if disponibilidas and disponibilidas[0] > 0:

            db.execute(SQL_DELETAR_TODAS_DISPONIBILIDADE_SEMANAL_PELA_SALA, (sala_id,))
            conexao.commit()
            return True
        
        return True
    
def alterar_disponibilidade_por_nome_e_sala_id(sala_id: int, disponibilidade: DisponibilidadeSemanalSala):
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db.execute(
            SQL_ALTERAR_DISPONIBILIDADE_PELO_DIA_E_SALA_ID, 
            (
                disponibilidade.horario_inicio,
                disponibilidade.horario_fim,
                disponibilidade.ativo,
                sala_id,
                disponibilidade.dia_da_semana
             )
        )
        conexao.commit()

def alterar_sala_pelo_id(sala: Sala) -> Sala | None:
    with obter_conexao() as conexao:
        db = conexao.cursor()
        db.execute(
            SQL_ALTERAR_SALA_PELO_ID, 
            (
                sala.nome,
                sala.capacidade,
                sala.bloco,
                sala.andar,
                sala.numero_sala,
                sala.tipo_sala,
                sala.observacoes,
                sala.status,
                sala.imagem,
                sala.intervalo_tempo,
                sala.id
             )
        )
        conexao.commit()