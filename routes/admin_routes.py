
from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse
from dtos.alterar_pedido_dto import AlterarPedidoDto
from dtos.alterar_produto_dto import AlterarProdutoDto
from dtos.entrar_dto import EntrarDto
from dtos.id_produto_dto import IdProdutoDTO
from dtos.inserir_produto_dto import InserirProdutoDTO
from dtos.problem_detail_dto import ProblemDetailsDto
from models.pedido_model import EstadoPedido
from models.produto_model import Produto
from repositories.pedido_repo import PedidoRepo
from repositories.produto_repo import ProdutoRepo
from repositories.usuario_repo import UsuarioRepo
from util.auth_jwt import conferir_senha, criar_token
from util.pydantic import create_validation_errors


router = APIRouter(prefix="/manager")

@router.get("/obter_produtos")
async def obter_produtos():
    produtos = ProdutoRepo.obter_todos()
    return produtos

@router.post("/inserir_produto", status_code= 201)
async def inserir_produto(inputDto: InserirProdutoDTO) -> Produto:
    novo_produto = Produto(None, inputDto.nome, inputDto.preco, inputDto.descricao, inputDto.estoque)
    novo_produto = ProdutoRepo.inserir(novo_produto)
    return novo_produto

@router.post("/excluir_produto", status_code = 204)
async def excluir_produto(inputDto: IdProdutoDTO):
    if ProdutoRepo.excluir(inputDto.id_produto):
        return None
    pd = ProblemDetailsDto("int", f"O produto com id {inputDto.id_produto} não foi encontrado", "value_not_found", ["body", "id_produto"])
    return JSONResponse(pd.to_dict(), status_code = 404)

@router.post("/alterar_produto", status_code = 204)
async def excluir_produto(inputDto: AlterarProdutoDto):
    produto_alterado = Produto(inputDto.id, inputDto.nome, inputDto.preco, inputDto.descricao, inputDto.estoque)
    if ProdutoRepo.alterar(produto_alterado):
        return produto_alterado

@router.get("/obter_produto/{id_produto}")
async def obter_produtos(id_produto: int = Path(..., title="Id do Produto", ge = 1)):
    produto = ProdutoRepo.obter_um(id_produto)
    if produto :
        return produto
    pd = ProblemDetailsDto("int", f"O produto com id {id_produto} não foi encontrado", "value_not_found", ["body", "id_produto"])
    return JSONResponse(pd.to_dict(), status_code = 404)


@router.post("/alterar_pedido", status_code= 204)
async def alterar_pedido(inputDto: AlterarPedidoDto):
    if PedidoRepo.alterar_estado(inputDto.id, inputDto.estado.value):
        return None
    pd = ProblemDetailsDto("int", f"O pedido com id {inputDto.id} não foi encontrado", "value_not_found", ["body", "id_produto"])
    return JSONResponse(pd.to_dict(), status_code = 404)


@router.get("/obter_pedido/{id_pedido}")
async def obter_pedidos(id_pedido: int = Path(..., title="Id do pedido", ge = 1)):
    pedido = PedidoRepo.obter_por_id(id_pedido)
    if pedido: return pedido
    pd = ProblemDetailsDto("int", f"O pedido com id {id_pedido} não foi encontrado", "value_not_found", ["body", "id_produto"])
    return JSONResponse(pd.to_dict(), status_code = 404)


@router.get("/obter_pedidos/{estado}")
async def obter_pedidos_por_estado(estado: EstadoPedido = Path(..., title="Id do pedido",)):
    pedidos = PedidoRepo.obter_todos_por_estado(estado.value)
    print(pedidos)
    if pedidos: return pedidos
    pd = ProblemDetailsDto("int", f"O pedido com id {estado} não foi encontrado", "value_not_found", ["body", "id_produto"])
    return JSONResponse(pd.to_dict(), status_code = 404)


@router.post("/entrar")
async def entrar(entrar_dto: EntrarDto):
    cliente_entrou = UsuarioRepo.obter_por_email(entrar_dto.email)
    if (
        (not cliente_entrou)
        or (not cliente_entrou.senha)
        or (not conferir_senha(entrar_dto.senha, cliente_entrou.senha))
    ):
        pd = ProblemDetailsDto("str", f"Credenciais inválidas, certifique-se que está cadastrado e de que sua senha está correta.", "value_not_found", ["body", "email", "senha"])
        return JSONResponse(pd.to_dict(), status_code = 404)

    token = criar_token(cliente_entrou.id, cliente_entrou.nome, cliente_entrou.email, cliente_entrou.perfil)
    return JSONResponse({"token": token})