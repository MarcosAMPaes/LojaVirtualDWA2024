SQL_CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS produto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_categoria INTEGER,
        nome TEXT NOT NULL,
        preco FLOAT NOT NULL,
        descricao TEXT NOT NULL,
        estoque INTEGER NOT NULL,
        FOREIGN KEY(id_categoria) REFERENCES categoria(id)
    )
"""

SQL_INSERIR = """
    INSERT INTO produto(id_categoria, nome, preco, descricao, estoque)
    VALUES (?, ?, ?, ?, ?)
"""

SQL_OBTER_TODOS = """
    SELECT p.id, p.id_categoria, p.nome, p.preco, p.descricao, p.estoque
    FROM produto p
    ORDER BY p.nome
"""

SQL_ALTERAR = """
    UPDATE produto
    SET id_categoria=?, nome=?, preco=?, descricao=?, estoque=?
    WHERE id=?
"""

SQL_EXCLUIR = """
    DELETE FROM produto    
    WHERE id=?
"""

SQL_OBTER_UM = """
    SELECT id, id_categoria, nome, preco, descricao, estoque
    FROM produto
    WHERE id=?
"""

SQL_OBTER_QUANTIDADE = """
    SELECT COUNT(*) FROM produto
"""

SQL_OBTER_BUSCA = """
    SELECT p.id, p.id_categoria, p.nome, p.preco, p.descricao, p.estoque
    FROM produto p
    WHERE p.nome LIKE ? OR p.descricao LIKE ?
    ORDER BY #1
    LIMIT ? OFFSET ?
"""

SQL_OBTER_QUANTIDADE_BUSCA = """
    SELECT COUNT(*) FROM produto
    WHERE nome LIKE ? OR descricao LIKE ?
"""

SQL_OBTER_POR_CATEGORIA = """
    SELECT p.id, p.id_categoria, p.nome, p.preco, p.descricao, p.estoque
    FROM produto p
    WHERE p.id_categoria=?
    ORDER BY p.nome
"""