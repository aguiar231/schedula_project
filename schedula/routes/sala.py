from datetime import datetime, timedelta
from http import HTTPStatus
import json
from typing import Annotated, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from schedula.models import DisponibilidadeSemanalSala, Usuario, Sala, ReservaSala
from schedula.repositories.sala import (
    alterar_status_reserva_confirmada,
    inserir_disponibilidade_semanal_padrao,
    inserir_sala,
    obter_contagem_reservas_por_usuario_com_filtro,
    obter_reservas_por_usuario,
    obter_reservas_por_usuario_paginado_com_filtro, 
    obter_sala_por_id,
    obter_contagem_salas_com_filtro,
    obter_salas_paginado_com_filtro,  
    obter_todas_salas,
    obter_tipos_salas, 
    obter_dias_semanas_disponivel_pelo_id, 
    verificar_conflito_reserva, 
    inserir_reserva_sala,
    deletar_sala_por_id,
    deletar_reservas_por_sala_id,
    deletar_disponibilidades_semanal_por_sala_id,
    alterar_disponibilidade_por_nome_e_sala_id,
    alterar_sala_pelo_id
)
from schedula.repositories.usuario import obter_usuario_por_id
from schedula.schemas import Disponibilidade
from schedula.security import obter_usuario_logado
from schedula.utils import redirecionar_com_toast, get_data_dia_semana, salvar_imagem_em_arquivo
from jinja2 import Environment

templates = Jinja2Templates(directory="./schedula/templates")

router = APIRouter(prefix="/sala", tags=["Sala"])

T_UsuarioLogado = Annotated[Usuario, Depends(obter_usuario_logado)]

def fromjson(value):
    return json.loads(value)

templates.env.filters['fromjson'] = fromjson

@router.get("/", response_class=HTMLResponse)
def listagem_salas(
        request: Request,
        usuario: T_UsuarioLogado,
        filter_nome: str  = Query(default=None),
        filter_tipo_sala: int|str = Query(default=None),
        filter_status: str = Query(default=None),
        page: int = Query(1, alias="pagina", ge=1), # pagina atual (padrão: 1)
):
    print(filter_nome, filter_tipo_sala, filter_status)
    if not usuario:
        return redirecionar_com_toast("/bem-vindo", toast={"mensagem": "Sem acesso!", "tipo": "aviso"})
    
    itens_por_pagina = 10
    total_salas = obter_contagem_salas_com_filtro(
        status=filter_status,
        tipo_sala=filter_tipo_sala
    )
    total_paginas = (total_salas + itens_por_pagina - 1) // itens_por_pagina

    salas = obter_salas_paginado_com_filtro(
        status=filter_status,
        tipo_sala=filter_tipo_sala,
        pagina=page,
        itens_por_pagina=itens_por_pagina
    )

    tipos_sala = obter_tipos_salas()
    dados = []
    for sala in salas:
        disponibilidades = obter_dias_semanas_disponivel_pelo_id(sala.id)
        dados.append({"sala": sala, "disponibilidades": disponibilidades})

    if filter_nome:
        salas = [sala for sala in salas if filter_nome.lower() in sala.nome.lower()]


    return templates.TemplateResponse("sala.html", {
        "request": request, 
        "usuario": usuario, 
        "salas": salas,
        "tipos_sala": tipos_sala,
        "total_paginas": total_paginas,
        "dados": dados,
        "pagina_atual": page,
        "titulo": "Salas :: Schedula"
    })

@router.post("/criar", response_class=HTMLResponse)
async def adicionar_sala(
    request: Request,
    usuario: T_UsuarioLogado,
    nome: str = Form(None),
    capacidade: str = Form(None),
    bloco: str = Form(None),
    andar: str = Form(None),
    numero_sala: str = Form(None),
    tipo_sala: str = Form(None),
    intervalo_tempo: str = Form(None),
    observacoes: str = Form(None),
    status: str = Form(None),
    imagem: UploadFile = File(None)
):
    
    capacidade = capacidade if capacidade != "" else None
    bloco = bloco if bloco != "" else None
    andar = andar if andar != "" else None
    bloco = bloco if bloco != "" else None
    observacoes = observacoes if observacoes != "" else None
    imagem = imagem if imagem.size > 1 else None

    if not usuario or usuario.administrador == 0:
        return redirecionar_com_toast("/sala", toast={"mensagem": "Somente um usuário administrador pode executar essa ação!", "tipo": "aviso"})
    
    if imagem:
        imagem_bytes = await imagem.read() 

        if not imagem_bytes:
            return redirecionar_com_toast("/sala", toast={"mensagem": "Imagem não é valida!", "tipo": "aviso"})
    
        imagem = salvar_imagem_em_arquivo(imagem_bytes, "./schedula/static/bucket/sala/")

    
    sala = inserir_sala(
        Sala(
            nome=nome,
            capacidade=capacidade,
            bloco=bloco,
            andar=andar,
            numero_sala=numero_sala,
            tipo_sala=tipo_sala,
            observacoes=observacoes,
            imagem=imagem,
            status=status,
            intervalo_tempo=intervalo_tempo
        )
    )
    inserir_disponibilidade_semanal_padrao(sala.id)

    return redirecionar_com_toast("/sala", toast={"mensagem": f"<b>{sala.nome.capitalize()}</b> <b style='color:green;'>adicionada</b> com sucesso!", "tipo": "bom"})
    
@router.post("/{sala_id}/editar")
async def editar_sala(
    request: Request,
    usuario: T_UsuarioLogado,
    sala_id: int,
    
    nome: str = Form(...),
    capacidade: int = Form(...),
    bloco: str = Form(...),
    andar: str = Form(...),
    numero_sala: int = Form(...),
    tipo_sala: int = Form(...),
    status: str = Form(...),
    imagem: UploadFile = File(None),
    observacoes: str = Form(...),
    intervalo_tempo: int = Form(None),
    
    segunda_ativo: bool = Form(None),
    segunda_inicio: str = Form(None),
    segunda_fim: str = Form(None),
    
    terca_ativo: bool = Form(None),
    terca_inicio: str = Form(None),
    terca_fim: str = Form(None),

    quarta_ativo: bool = Form(None),
    quarta_inicio: str = Form(None),
    quarta_fim: str = Form(None),

    quinta_ativo: bool = Form(None),
    quinta_inicio: str = Form(None),
    quinta_fim: str = Form(None),

    sexta_ativo: bool = Form(None),
    sexta_inicio: str = Form(None),
    sexta_fim: str = Form(None),

    sabado_ativo: bool = Form(None),
    sabado_inicio: str = Form(None),
    sabado_fim: str = Form(None),

    domingo_ativo: bool = Form(None),
    domingo_inicio: str = Form(None),
    domingo_fim: str = Form(None),
):
    imagem = imagem if imagem.size > 1 else None

    disponibilidades = [
            DisponibilidadeSemanalSala(
                dia_da_semana="SEGUNDA",
                horario_inicio=segunda_inicio,
                horario_fim=segunda_fim,
                ativo=segunda_ativo if segunda_ativo else 0,
                
            ),
            DisponibilidadeSemanalSala(
                dia_da_semana="TERÇA",
                horario_inicio=terca_inicio,
                horario_fim=terca_fim,
                ativo=terca_ativo if terca_ativo else 0,
                
            ),
            DisponibilidadeSemanalSala(
                dia_da_semana="QUARTA",
                horario_inicio=quarta_inicio,
                horario_fim=quarta_fim,
                ativo=quarta_ativo if quarta_ativo else 0,
                
            ),
            DisponibilidadeSemanalSala(
                dia_da_semana="QUINTA",
                horario_inicio=quinta_inicio,
                horario_fim=quinta_fim,
                ativo=quinta_ativo if quinta_ativo else 0,
                
            ),
            DisponibilidadeSemanalSala(
                dia_da_semana="SEXTA",
                horario_inicio=sexta_inicio,
                horario_fim=sexta_fim,
                ativo=sexta_ativo if sexta_ativo else 0,
                
            ),
            DisponibilidadeSemanalSala(
                dia_da_semana="SÁBADO",
                horario_inicio=sabado_inicio,
                horario_fim=sabado_fim,
                ativo=sabado_ativo if sabado_ativo else 0,
                
            ),
            DisponibilidadeSemanalSala(
                dia_da_semana="DOMINGO",
                horario_inicio=domingo_inicio,
                horario_fim=domingo_fim,
                ativo=domingo_ativo if domingo_ativo else 0,
            ),
    ]
    if imagem:
        imagem_bytes = await imagem.read() 

        if not imagem_bytes:
            return redirecionar_com_toast("/sala", toast={"mensagem": "Imagem não é valida!", "tipo": "aviso"})
    
        imagem = salvar_imagem_em_arquivo(imagem_bytes, "./schedula/static/bucket/sala/")

    for disponibilidade in disponibilidades:
        alterar_disponibilidade_por_nome_e_sala_id(sala_id, disponibilidade)

    print(f"Nome da Sala: {nome}")
    print(f"Capacidade: {capacidade}")
    print(f"Bloco: {bloco}")
    print(f"Andar: {andar}")
    print(f"Número da Sala: {numero_sala}")
    print(f"Tipo de Sala: {tipo_sala}")
    print(f"Status: {status}")
    print(f"Observações: {observacoes}")
    print(f"Disponibilidade: {disponibilidades}")
    
    sala = Sala(
        id=sala_id,
        nome=nome,
        capacidade=capacidade,
        bloco=bloco,
        andar=andar,
        numero_sala=numero_sala,
        tipo_sala=tipo_sala,
        observacoes=observacoes,
        imagem=imagem,
        status=status,
        intervalo_tempo=intervalo_tempo
    )
    alterar_sala_pelo_id(sala)   

    return redirecionar_com_toast("/sala", toast={"mensagem": "Sala Atualizada!", "tipo": "bom"}) 
    
@router.post("/{sala_id}/excluir")
def deletar_sala(
    request: Request,
    usuario: T_UsuarioLogado,
    sala_id: int
):
    if not usuario or usuario.administrador == 0:
        return redirecionar_com_toast("/sala", toast={"mensagem": "Somente um usuário administrador pode executar essa ação!", "tipo": "aviso"})
    
    reserva = deletar_reservas_por_sala_id(sala_id)
    disponibilidade_semanal = deletar_disponibilidades_semanal_por_sala_id(sala_id)
    sala = obter_sala_por_id(sala_id)
    deletar_sala = deletar_sala_por_id(sala_id)
    
    if not reserva:
        return redirecionar_com_toast("/sala", toast={"mensagem": "Não foi possivel excluir sala, porque houve um erro ao deletar as reservas dessa sala!", "tipo": "bom"})
    
    if not disponibilidade_semanal:
        return redirecionar_com_toast("/sala", toast={"mensagem": "Não foi possivel excluir sala, porque houve um erro ao deletar as disponibilidades dessa sala!", "tipo": "bom"})

    if not deletar_sala:
        return redirecionar_com_toast("/sala", toast={"mensagem": "Houve um erro ao excluir a sala!", "tipo": "bom"})
    
    return redirecionar_com_toast("/sala", toast={"mensagem": f"<b>{sala.nome.capitalize()}</b> excluído com sucesso!", "tipo": "bom"})

@router.get("/{sala_id}/horario", response_class=HTMLResponse)
def listagem_horarios(
        request: Request,
        usuario: T_UsuarioLogado,
        sala_id: int,
        filter_data: str = Query(default=None)
):
    if not usuario:
        return redirecionar_com_toast("/bem-vindo", toast={"mensagem": "Sem acesso!", "tipo": "aviso"})
    
    if not sala_id:
        return redirecionar_com_toast("/sala", toast={"mensagem": "Precisa selecionar uma sala válida!", "tipo": "aviso"})
    
    if not filter_data:
        filter_data = datetime.now().strftime("%d-%m-%Y")
    
    data_oferecida = datetime.strptime(filter_data, "%d-%m-%Y")
    hoje = datetime.now()
    print(hoje)

    sala = obter_sala_por_id(sala_id)

    if not sala:
        return redirecionar_com_toast("/sala", toast={"mensagem": "Precisa selecionar uma sala válida!", "tipo": "aviso"})

    tipos_sala = obter_tipos_salas()
    dias_semana = obter_dias_semanas_disponivel_pelo_id(sala.id)   
    horarios_por_dia = []
    
    for dia in dias_semana:
        data_dia_semana = get_data_dia_semana(dia.dia_da_semana, data_oferecida)
        horario_inicio = datetime.strptime(dia.horario_inicio, "%H:%M")
        horario_fim = datetime.strptime(dia.horario_fim, "%H:%M")
        intervalo_tempo = timedelta(minutes=sala.intervalo_tempo)

        horarios = []
        while horario_inicio < horario_fim:
            proximo_horario = horario_inicio + intervalo_tempo
            horario_intervalo = f"{datetime.strftime(horario_inicio, '%H:%M')} - {datetime.strftime(proximo_horario, '%H:%M')}"

            if data_dia_semana.date() < hoje.date() or (data_dia_semana.date() == hoje.date() and horario_inicio.time() < hoje.time()):
                ativo = 0
        
            else:
                reserva = ReservaSala(
                        usuario_id=usuario.id,
                        sala_id=sala.id,
                        horario_inicio=horario_inicio.time(),
                        horario_fim=proximo_horario.time(),
                        data_reserva=data_dia_semana.date()
                    )
                if verificar_conflito_reserva(reserva):
                    ativo = 0
                    
                else: 
                    ativo = dia.ativo

            horarios.append({
                "time": horario_intervalo,
                "ativo": ativo
            })
            horario_inicio = proximo_horario

        horarios_por_dia.append({
            "dia": dia.dia_da_semana,
            "data": data_dia_semana.strftime("%d-%m-%Y"),
            "horarios": horarios
        })
    return templates.TemplateResponse("horario.html", {
        "request": request, 
        "usuario": usuario,
        "sala": sala,
        "dias_semana": horarios_por_dia,
        "tipos_sala": tipos_sala,
        "titulo": "Salas :: Schedula"
    })

@router.post("/{sala_id}/horario/agendar")
def marcar_reserva(
    usuario: T_UsuarioLogado,
    sala_id: int,
    horarios: List[str] = Form(...)
):
    if not usuario:
        return redirecionar_com_toast("/bem-vindo", toast={"mensagem": "Sem acesso!", "tipo": "aviso"})
    
    if not sala_id:
        return redirecionar_com_toast("/sala", toast={"mensagem": "Precisa selecionar uma sala válida!", "tipo": "aviso"})
    
    sala = obter_sala_por_id(sala_id)

    reservas = []
    for horario in horarios:
        horario = json.loads(horario.replace("'", '"'))
        print(horario)
        reserva=ReservaSala(
            usuario_id=usuario.id,
            sala_id=sala.id,
            horario_inicio=datetime.strptime(horario["time"].split(" - ")[0], "%H:%M").time(),
            horario_fim=datetime.strptime(horario["time"].split(" - ")[1], "%H:%M").time(),
            data_reserva=datetime.strptime(horario["date"], "%d-%m-%Y").date(),
            status="PENDENTE"
        )
        if verificar_conflito_reserva(reserva):
            return redirecionar_com_toast(
                f"/sala/{sala_id}/horario", 
                toast={
                    "mensagem": f"O Horario <b>{horario['time'].split(' - ')[0]}</b> à <b>{horario['time'].split(' - ')[1]}</b> não está disponivel", 
                    "tipo": "aviso"
                }
            )
            
        reservas.append(reserva)
        
    for reserva in reservas:
        inserir_reserva_sala(reserva)
        response = redirecionar_com_toast(
            f"/sala/{sala_id}/horario", 
            toast={
                "mensagem": f"Sala <b>{sala.nome}</b> reservada para <b>{datetime.strftime(reserva.data_reserva, '%d-%m-%Y')} {reserva.horario_inicio.strftime('%H:%M')}</b>", 
                "tipo": "aviso"
            }
        )


    return response

@router.get("/reserva") 
def listar_reservas(
    request: Request,
    usuario: T_UsuarioLogado,
    filter_data_reserva: str = Query(None),
    filter_status: str = Query(None),
    page: int = Query(1, alias="pagina", ge=1),  # pagina atual (padrão: 1)
    
):
    if not usuario:
        return redirecionar_com_toast("/bem-vindo", toast={"mensagem": "Sem acesso!", "tipo": "aviso"})
    
    if filter_data_reserva:
        print(f"Filtro data {filter_data_reserva}")
    
    if filter_status:
        print(f"Filtro status {filter_status}")

    itens_por_pagina = 10  # Quantidade de itens por página
    # Obter total de reservas com os filtros aplicados
    total_reservas = obter_contagem_reservas_por_usuario_com_filtro(usuario.id, filter_data_reserva, filter_status)
    total_paginas = (total_reservas + itens_por_pagina - 1) // itens_por_pagina

    # Obter reservas com paginação e filtros aplicados
    reservas = obter_reservas_por_usuario_paginado_com_filtro(
        usuario_id=usuario.id, 
        data_reserva=filter_data_reserva, 
        status=filter_status, 
        pagina=page,
        itens_por_pagina=itens_por_pagina
    )
    
    dados = []
    for reserva in reservas:
        sala = obter_sala_por_id(reserva.sala_id)     
        dados.append({"sala": sala, "reserva": reserva, "usuario": usuario})

    return templates.TemplateResponse("reserva.html", {
        "request": request, 
        "usuario": usuario,
        "dados" : dados,
        "titulo": "Salas :: Schedula",
        "pagina_atual": page,
        "total_paginas": total_paginas
    })

@router.post("/reserva/{reserva_id}/confirmar")
def confirmar_reserva(
    request: Request,
    usuario: T_UsuarioLogado,
    reserva_id: int
):
    if not usuario:
        return redirecionar_com_toast("/bem-vindo", toast={"mensagem": "Sem acesso!", "tipo": "aviso"})
    

    alterar_status_reserva_confirmada("CONFIRMADA", reserva_id)
    response = redirecionar_com_toast("/sala/reserva", toast={"mensagem": "Reserva <b style='color:green;'>Confirmada</b> com sucesso ✅", "tipo": "bom"}) 
    return response

@router.post("/reserva/{reserva_id}/cancelar")
def cancelar_reserva(
    request: Request,
    usuario: T_UsuarioLogado,
    reserva_id: int
):
    if not usuario:
        return redirecionar_com_toast("/bem-vindo", toast={"mensagem": "Sem acesso!", "tipo": "aviso"})
    
    alterar_status_reserva_confirmada("CANCELADA", reserva_id)
    response = redirecionar_com_toast("/sala/reserva", toast={"mensagem": "Reserva <b style='color:red;'>Cancelada</b> com sucesso ✅", "tipo": "bom"}) 
    return response

