from dataclasses import dataclass
import datetime
from enum import Enum


class SalaStatus(str, Enum):
    disponivel = "DISPONIVEL"
    desativada = "DESATIVADA"

class DiasSemana(str, Enum):
    domingo = "DOMINGO"
    segunda = "SEGUNDA"
    terca = "TERÇA"
    quarta = "QUARTA"
    quinta = "QUINTA"
    sexta = "SEXTA"
    sabado = "SABADO"

class ReservaStatus(str, Enum):
    confirmado = "CONFIRMADA"
    cancelada = "CANCELADA"
    pendente = "PENDENTE"


@dataclass
class Usuario:
    id: int | None = None
    nome: str | None = None
    email: str | None = None
    token: str | None = None
    senha: str | None = None
    administrador: int | None = None
    telefone: str | None = None
    ativo: bool | None = None
    imagem: str | None = None
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime  | None = None

@dataclass
class TipoSala:
    id : int | None = None
    nome: str | None = None

@dataclass
class Sala:
    id: int | None = None
    nome: str | None = None
    capacidade: int | None = None
    bloco: str | None = None
    andar: str | None = None
    numero_sala: int | None = None
    tipo_sala: int | None = None
    observacoes: str | None = None
    imagem: str | None = None
    status: SalaStatus | None = None
    intervalo_tempo: int | None = None
    created_at: datetime.datetime  | None = None
    updated_at: datetime.datetime  | None = None

@dataclass
class DisponibilidadeSemanalSala:
    id: int | None = None
    sala_id: int | None = None
    dia_da_semana: str | None = None
    horario_inicio: datetime.time | None = None
    horario_fim: datetime.time | None = None
    ativo: bool | None = None
    created_at: datetime.datetime  | None = None
    updated_at: datetime.datetime  | None = None

@dataclass
class ReservaSala:
    id: int | None = None
    usuario_id: int | None = None
    sala_id: int | None = None
    data_reserva: datetime.date | None = None
    horario_inicio: datetime.time | None = None
    horario_fim: datetime.time | None = None
    status: ReservaStatus | None = None
    created_at: datetime.datetime  | None = None
    updated_at: datetime.datetime | None = None
