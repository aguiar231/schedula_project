SQL_INSERIR_SALA = """
    INSERT INTO sala (
        nome, 
        capacidade, 
        bloco, 
        andar, 
        numero_sala, 
        tipo_sala, 
        observacoes,
        imagem, 
        status, 
        intervalo_tempo
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

SQL_INSERIR_DISPONIBILIDADE_SEMANAL_PADRAO = """
    INSERT INTO disponibilidade_semanal_sala (sala_id, dia_da_semana, horario_inicio, horario_fim, ativo)
    VALUES (?, ?, ?, ?, ?)
        
"""

SQL_INSERIR_RESERVA_SALA = """
    INSERT INTO reserva_sala (
        usuario_id, sala_id, data_reserva, horario_inicio, horario_fim, status
    ) VALUES (?, ?, ?, ?, ?, ?)
"""

SQL_VERIFICAR_CONFLITOS_RESERVA = """
    SELECT 
        id, usuario_id, sala_id, data_reserva, horario_inicio, horario_fim, status
    FROM 
        reserva_sala
    WHERE 
        sala_id = ? 
        AND data_reserva = ? 
        AND status != 'CANCELADA'
        AND (
            (horario_inicio < ? AND horario_fim > ?) -- Novo horário começa dentro de uma reserva existente
            OR 
            (horario_inicio < ? AND horario_fim > ?) -- Novo horário termina dentro de uma reserva existente
            OR 
            (horario_inicio >= ? AND horario_fim <= ?) -- Novo horário engloba completamente uma reserva existente
    );
"""

SQL_OBTER_TODAS_SALAS = """
    SELECT *
    FROM sala
    ORDER BY nome
"""

SQL_OBTER_POR_ID_SALA = """
    SELECT *
    FROM sala
    WHERE id=?
"""

SQL_FILTRAR_SALAS_PELO_NOME = """
    SELECT *
    FROM sala
    WHERE nome LIKE ?
"""

SQL_OBTER_TODOS_TIPO_SALA = """
    SELECT *
    FROM tipo_sala
    ORDER BY nome
"""

SQL_OBTER_DISPONIBILIDADE_SEMANAL_PELO_SALA_ID = """
    SELECT *
    FROM disponibilidade_semanal_sala
    WHERE sala_id=?
    ORDER BY id
"""

SQL_CONTAR_DISPONIBILIDADE_SEMANAL_PELO_SALA_ID_POR_SALA = """
    SELECT COUNT(*) FROM disponibilidade_semanal_sala WHERE sala_id = ?;

"""

SQL_OBTER_RESERVAS_PELO_USUARIO_ID = """
    SELECT *
    FROM reserva_sala
    WHERE usuario_id=?
"""

SQL_OBTER_RESERVAS_PELO_STATUS= """
    SELECT *
    FROM reserva_sala
    WHERE status=?
"""

SQL_OBTER_RESERVAS= """
    SELECT *
    FROM reserva_sala
    ORDER BY 
        CASE 
            WHEN status = 'PENDENTE' THEN 1
            WHEN status = 'CONFIRMADA' THEN 2
            WHEN status = 'CANCELADA' THEN 3
            ELSE 4 -- para nao quebrar KKKKKK
        END
"""
SQL_CONTAR_RESERVAS_POR_SALA = """
    SELECT COUNT(*) FROM reserva_sala WHERE sala_id = ?;

"""


SQL_OBTER_RESERVAS_PAGINADO_PELO_USUARIO_ID =  """
    SELECT *
    FROM reserva_sala
    WHERE usuario_id = ?
"""

SQL_CONTAR_RESERVAS = """
    SELECT COUNT(*) FROM reserva_sala WHERE usuario_id = ?
"""

SQL_CONTAR_SALAS = """
    SELECT COUNT(*) FROM sala WHERE 1=1
"""

SQL_OBTER_SALAS_PAGINADA = """
    SELECT * FROM sala WHERE 1=1
"""

SQL_ALTERAR_STATUS_RESERVA = """
    UPDATE reserva_sala
    SET status = ?
    WHERE id = ?;
"""

SQL_ALTERAR_DISPONIBILIDADE_PELO_DIA_E_SALA_ID = """
    UPDATE disponibilidade_semanal_sala
    SET
        horario_inicio = COALESCE(?, horario_inicio),
        horario_fim = COALESCE(?, horario_fim),
        ativo = COALESCE(?, ativo)
    WHERE sala_id = ? AND dia_da_semana = ?
"""

SQL_ALTERAR_SALA_PELO_ID = """
    UPDATE sala
    SET
        nome = COALESCE(?, nome),
        capacidade = COALESCE(?, capacidade),
        bloco = COALESCE(?, bloco),
        andar = COALESCE(?, andar),
        numero_sala = COALESCE(?, numero_sala),
        tipo_sala = COALESCE(?, tipo_sala),
        observacoes = COALESCE(?, observacoes),
        status = COALESCE(?, status),
        imagem = COALESCE(?, imagem),
        intervalo_tempo = COALESCE(?, intervalo_tempo)

    WHERE id = ?
"""

SQL_DELETAR_SALA_POR_ID = """
    DELETE FROM sala WHERE id = ?
"""

SQL_DELETAR_TODAS_RESERVAS_PELA_SALA = """
    DELETE FROM reserva_sala WHERE sala_id = ?
"""

SQL_DELETAR_TODAS_DISPONIBILIDADE_SEMANAL_PELA_SALA = """
    DELETE FROM disponibilidade_semanal_sala WHERE sala_id = ?
"""