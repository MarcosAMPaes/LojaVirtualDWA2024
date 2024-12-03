import asyncio
from io import BytesIO
from PIL import Image
from typing import List, Optional
from fastapi import APIRouter, Body, File, Form, Path, UploadFile
from fastapi.responses import JSONResponse

from dtos.alterar_pedido_dto import AlterarPedidoDto
from dtos.alterar_produto_dto import AlterarProdutoDto
from dtos.inserir_categoria_dto import InserirCategoriaDto
from dtos.inserir_produto_dto import InserirProdutoDto
from dtos.problem_details_dto import ProblemDetailsDto
from models.categoria_model import Categoria
from models.pedido_model import EstadoPedido
from models.produto_model import Produto
from models.usuario_model import Usuario
from repositories.categoria_repo import CategoriaRepo
from repositories.item_pedido_repo import ItemPedidoRepo
from repositories.pedido_repo import PedidoRepo
from repositories.produto_repo import ProdutoRepo
from repositories.usuario_repo import UsuarioRepo
from util.images import transformar_em_quadrada

SLEEP_TIME = 0.2
router = APIRouter(prefix="/admin")


@router.get("/obter_produtos")
async def obter_produtos():
    await asyncio.sleep(SLEEP_TIME)
    produtos = ProdutoRepo.obter_todos()
    return produtos


@router.post("/inserir_produto", status_code=201)
async def inserir_produto(nome: str = Form(...),
                          id_categoria: int = Form(...),
                          preco: float = Form(...),
                          descricao: str = Form(...),
                          estoque: int = Form(...),
                          imagem: Optional[UploadFile] = File(None)):
    produto_dto = InserirProdutoDto(
         nome= nome,
         id_categoria= id_categoria,
         preco= preco,
         descricao= descricao,
         estoque= estoque
    )
    try:
        conteudo_arquivo = await imagem.read()
    except Exception:
        print("O arquivo enviado nao é uma imagem valida.")
    imagem = Image.open(BytesIO(conteudo_arquivo))
    if not imagem:
        pd = ProblemDetailsDto(
            "int",
            "O arquivo enviado nao é uma imagem válida.",
            "invalid_format",
            ["body", "imagem"],
        )
        return JSONResponse(pd.to_dict(), status_code=422)
    await asyncio.sleep(SLEEP_TIME)
    novo_produto = Produto(None, produto_dto.id_categoria, produto_dto.nome, produto_dto.preco, produto_dto.descricao, produto_dto.estoque)
    novo_produto = ProdutoRepo.inserir(novo_produto)
    if novo_produto:
        imagem_quadrada = transformar_em_quadrada(imagem)
        imagem_quadrada.save("static/img/produtos/{id:04d}.jpg", "JPEG", optimize=True)
        return novo_produto
    pd = ProblemDetailsDto(
        "int",
        f"O produto com id <b>{novo_produto.id}</b> foi criado.",
        "value_not_found",
        ["body", "id_produto"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)

@router.post("/excluir_produto", status_code=204)
async def excluir_produto(id_produto: int = Form(..., title="Id do Produto", ge=1)):
    await asyncio.sleep(SLEEP_TIME)
    if ProdutoRepo.excluir(id_produto):
        return None
    pd = ProblemDetailsDto(
        "int",
        f"O produto com id <b>{id_produto}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id_produto"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.get("/obter_produto/{id_produto}")
async def obter_produto(id_produto: int = Path(..., title="Id do Produto", ge=1)):
    await asyncio.sleep(SLEEP_TIME)
    produto = ProdutoRepo.obter_um(id_produto)
    if produto:
        return produto
    pd = ProblemDetailsDto(
        "int",
        f"O produto com id <b>{id_produto}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id_produto"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.post("/alterar_produto", status_code=204)
async def alterar_produto(inputDto: AlterarProdutoDto):
    await asyncio.sleep(SLEEP_TIME)
    produto = Produto(
        inputDto.id, inputDto.id_categoria, inputDto.nome, inputDto.preco, inputDto.descricao, inputDto.estoque
    )
    if ProdutoRepo.alterar(produto):
        return None
    pd = ProblemDetailsDto(
        "int",
        f"O produto com id <b>{inputDto.id}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.post("/alterar_pedido", status_code=204)
async def alterar_pedido(inputDto: AlterarPedidoDto):
    await asyncio.sleep(SLEEP_TIME)
    if PedidoRepo.alterar_estado(inputDto.id, inputDto.estado.value):
        return None
    pd = ProblemDetailsDto(
        "int",
        f"O pedido com id <b>{inputDto.id}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.post("/cancelar_pedido", status_code=204)
async def cancelar_pedido(id_pedido: int = Form(..., title="Id do Pedido", ge=1)):
    await asyncio.sleep(SLEEP_TIME)
    if PedidoRepo.alterar_estado(id_pedido, EstadoPedido.CANCELADO.value):
        return None
    pd = ProblemDetailsDto(
        "int",
        f"O pedido com id <b>{id_pedido}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.post("/evoluir_pedido", status_code=204)
async def evoluir_pedido(id_pedido: int = Form(..., title="Id do Pedido", ge=1)):
    await asyncio.sleep(SLEEP_TIME)
    pedido = PedidoRepo.obter_por_id(id_pedido)
    if not pedido:
        pd = ProblemDetailsDto(
            "int",
            f"O pedido com id <b>{id_pedido}</b> não foi encontrado.",
            "value_not_found",
            ["body", "id"],
        )
        return JSONResponse(pd.to_dict(), status_code=404)
    estado_atual = pedido.estado
    estados = [e.value for e in list(EstadoPedido) if e != EstadoPedido.CANCELADO]
    indice = estados.index(estado_atual)
    indice += 1
    if indice < len(estados):
        novo_estado = estados[indice]
        if PedidoRepo.alterar_estado(id_pedido, novo_estado):
            return None
    pd = ProblemDetailsDto(
        "int",
        f"O pedido com id <b>{id_pedido}</b> não pode ter seu estado evoluído para <b>cancelado</b>.",
        "state_change_invalid",
        ["body", "id"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.get("/obter_pedido/{id_pedido}")
async def obter_pedido(id_pedido: int = Path(..., title="Id do Pedido", ge=1)):
    # TODO: refatorar criando Dto com resultado específico
    await asyncio.sleep(SLEEP_TIME)
    pedido = PedidoRepo.obter_por_id(id_pedido)
    if pedido:
        itens = ItemPedidoRepo.obter_por_pedido(pedido.id)
        cliente = UsuarioRepo.obter_por_id(pedido.id_cliente)
        pedido.itens = itens
        pedido.cliente = cliente
        return pedido
    pd = ProblemDetailsDto(
        "int",
        f"O pedido com id <b>{id_pedido}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.get("/obter_pedidos_por_estado/{estado}")
async def obter_pedidos_por_estado(
    estado: EstadoPedido = Path(..., title="Estado do Pedido")
):
    await asyncio.sleep(SLEEP_TIME)
    pedidos = PedidoRepo.obter_todos_por_estado(estado.value)
    return pedidos


@router.get("/obter_usuarios")
async def obter_usuarios() -> List[Usuario]:
    await asyncio.sleep(SLEEP_TIME)
    usuarios = UsuarioRepo.obter_todos()
    return usuarios


@router.post("/excluir_usuario", status_code=204)
async def excluir_usuario(id_usuario: int = Form(...)):
    await asyncio.sleep(SLEEP_TIME)
    if UsuarioRepo.excluir(id_usuario):
        return None
    pd = ProblemDetailsDto(
        "int",
        f"O usuario com id <b>{id_usuario}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id_produto"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)

@router.get("/obter_categorias")
async def obter_categorias() -> List[Categoria]:
    await asyncio.sleep(SLEEP_TIME)
    categorias = CategoriaRepo.obter_todos()
    return categorias

@router.post("/excluir_categoria", status_code=204)
async def excluir_categoria(id_categoria: int = Form(...)):
    await asyncio.sleep(SLEEP_TIME)
    if CategoriaRepo.excluir(id_categoria):
        return None
    pd = ProblemDetailsDto(
        "int",
        f"A categoria com id <b>{id_categoria}</b> não foi encontrada.",
        "value_not_found",
        ["body", "id_categoria"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.post("/inserir_categoria", status_code=201)
async def inserir_produto(nome: str = Form(...),
                          descricao: str = Form(...)):
    categoria_dto = InserirCategoriaDto(
         nome= nome,
         descricao= descricao
    )
    nova_categoria = Categoria(None, categoria_dto.nome, categoria_dto.descricao)
    nova_categoria = CategoriaRepo.inserir(nova_categoria)
    if nova_categoria:
        return nova_categoria
    pd = ProblemDetailsDto(
        "int",
        "Ocorreu um erro ao inserir a categoria.",
        "insert_error",
        ["body", "nome"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)

@router.get("/obter_categoria/{id_categoria}")
async def obter_categoria(id_categoria: int = Path(..., title="Id da Categoria", ge=1)):
    await asyncio.sleep(SLEEP_TIME)
    categoria = CategoriaRepo.obter_um(id_categoria)
    return categoria
    
@router.post("/alterar_categoria", status_code=204)
async def alterar_categoria(
    id: int = Form(...),
    nome: str = Form(...),
    descricao: str = Form(...),
):
    await asyncio.sleep(SLEEP_TIME)
    categoria = Categoria(id, nome, descricao)
    if CategoriaRepo.alterar(categoria):
        return None
    pd = ProblemDetailsDto(
        "int",
        f"A categoria com id <b>{id}</b> não foi encontrada.",
        "value_not_found",
        ["body", "id"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)