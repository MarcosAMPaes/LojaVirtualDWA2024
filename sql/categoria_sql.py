SQL_CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS categoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT NOT NULL
    )
"""

SQL_INSERIR = """
    INSERT INTO categoria(nome, descricao)
    VALUES (?, ?)
"""

SQL_OBTER_TODOS = """
    SELECT id, nome, descricao
    FROM categoria
    ORDER BY nome
"""

SQL_ALTERAR = """
    UPDATE categoria
    SET nome=?, descricao=?
    WHERE id=?
"""

SQL_EXCLUIR = """
    DELETE FROM categoria    
    WHERE id=?
"""

SQL_OBTER_UM = """
    SELECT id, nome, descricao
    FROM categoria
    WHERE id=?
"""

SQL_OBTER_QUANTIDADE = """
    SELECT COUNT(*) FROM categoria
"""

SQL_OBTER_BUSCA = """
    SELECT id, nome, descricao
    FROM categoria
    WHERE nome LIKE ? OR descricao LIKE ?
    ORDER BY #1
    LIMIT ? OFFSET ?
"""

SQL_OBTER_QUANTIDADE_BUSCA = """
    SELECT COUNT(*) FROM categoria
    WHERE nome LIKE ? OR descricao LIKE ?
"""