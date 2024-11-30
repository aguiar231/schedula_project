SQL_CREATE_TABLES = """
    CREATE TABLE IF NOT EXISTS usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        token TEXT NULL,
        senha TEXT NOT NULL,
        administrador INT NOT NULL,
        telefone TEXT NULL,
        ativo BOOLEAN NOT NULL DEFAULT 1,
        imagem TEXT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tipo_sala (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS sala (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        capacidade INTEGER,
        bloco TEXT NULL,
        andar TEXT NULL,
        numero_sala INTEGER NULL,
        tipo_sala INTEGER NOT NULL,
        observacoes TEXT,
        imagem TEXT NULL,
        status TEXT NOT NULL DEFAULT 'DISPONIVEL' CHECK (status IN ('DISPONIVEL', 'INDISPONIVEL')),
        intervalo_tempo INTEGER NOT NULL DEFAULT 60,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tipo_sala) REFERENCES tipo_sala (id)
    );

    CREATE TABLE IF NOT EXISTS disponibilidade_semanal_sala (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sala_id INTEGER NOT NULL,
        dia_da_semana TEXT NOT NULL CHECK (dia_da_semana IN ('DOMINGO', 'SEGUNDA', 'TERÇA', 'QUARTA', 'QUINTA', 'SEXTA', 'SÁBADO')),
        horario_inicio TIME NOT NULL,
        horario_fim TIME NOT NULL,
        ativo BOOLEAN NOT NULL DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sala_id) REFERENCES sala (id)
    );

    CREATE TABLE IF NOT EXISTS reserva_sala (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        sala_id INTEGER NOT NULL,
        data_reserva DATE NOT NULL,
        horario_inicio TIME NOT NULL,
        horario_fim TIME NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDENTE' CHECK (status IN ('CONFIRMADA', 'CANCELADA', 'PENDENTE')),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuario (id),
        FOREIGN KEY (sala_id) REFERENCES sala (id)
    );
"""