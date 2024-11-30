from pydantic import BaseModel

class DisponibilidadeDia(BaseModel):
    id: int
    ativo: bool
    horario_inicio: str
    horario_fim: str

class Disponibilidade(BaseModel):
    segunda: DisponibilidadeDia
    terca: DisponibilidadeDia
    quarta: DisponibilidadeDia
    quinta: DisponibilidadeDia
    sexta: DisponibilidadeDia
    sabado: DisponibilidadeDia
    domingo: DisponibilidadeDia