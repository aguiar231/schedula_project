SQL_CRIAR_SALAS_TEST = """
INSERT INTO sala (
        nome, capacidade, bloco, andar, numero_sala, tipo_sala, observacoes, intervalo_tempo
    ) VALUES (Sala Schedula, 20, 1, 1, 1, 1, "Boas Vindas ao Schedula!", 1)
"""

SQL_CRIAR_TIPOS_SALAS_DEFAULT = """
INSERT INTO tipo_sala (nome) VALUES 'Aula'
INSERT INTO tipo_sala (nome) VALUES 'Reunião'
INSERT INTO tipo_sala (nome) VALUES 'Laboratório'
"""

SQL_CRIAR_USER_ADMINISTRADOR_DEFAULT = """
INSERT INTO usuario (nome, email, senha, administrador) 
VALUES (?, ?, ?, ?);
"""