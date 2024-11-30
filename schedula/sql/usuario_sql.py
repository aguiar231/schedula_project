SQL_INSERIR = """
    INSERT INTO usuario (nome, email, senha, administrador)
    VALUES (?, ?, ?, ?)
"""

SQL_ALTERAR = """
    UPDATE usuario
    SET 
        nome = COALESCE(?, nome),
        email = COALESCE(?, email),
        telefone = COALESCE(?, telefone),
        senha = COALESCE(?, senha),
        imagem = COALESCE(?, imagem)
    WHERE id = ?;
"""

SQL_ALTERAR_SENHA = """
    UPDATE usuario SET senha=?
    WHERE id=?
"""

SQL_ALTERAR_TOKEN = """
    UPDATE usuario SET token=?
    WHERE id=?
"""

SQL_EXCLUIR = """
    DELETE FROM usuario
    WHERE id=?
"""

SQL_OBTER_POR_ID = """
    SELECT *
    FROM usuario
    WHERE id=?
"""

SQL_OBTER_USUARIO_POR_EMAIL = """
    SELECT *
    FROM usuario
    WHERE email=?
"""

SQL_OBTER_POR_TOKEN = """
    SELECT id, nome, email, token, senha, administrador, telefone, ativo, imagem, created_at, updated_at
    FROM usuario
    WHERE token=?
"""

SQL_OBTER_TODOS = """
    SELECT *
    FROM usuario
    ORDER BY nome
"""