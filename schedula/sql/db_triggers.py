SQL_CRIAR_TRIGGERS = """
    CREATE TRIGGER update_usuario_updated_at
    AFTER UPDATE ON usuario
    FOR EACH ROW
    BEGIN
        UPDATE usuario SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;

    CREATE TRIGGER update_sala_updated_at
    AFTER UPDATE ON sala
    FOR EACH ROW
    BEGIN
        UPDATE sala SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;

    CREATE TRIGGER update_disponibilidade_semanal_sala_updated_at
    AFTER UPDATE ON disponibilidade_semanal_sala
    FOR EACH ROW
    BEGIN
        UPDATE disponibilidade_semanal_sala SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;

    CREATE TRIGGER update_reserva_sala_updated_at
    AFTER UPDATE ON reserva_sala
    FOR EACH ROW
    BEGIN
        UPDATE reserva_sala SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;

    CREATE TRIGGER update_tipo_sala_at
    AFTER UPDATE ON tipo_sala
    FOR EACH ROW
    BEGIN
        UPDATE tipo_sala SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
"""