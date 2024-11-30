import json
import random
import sqlite3
import io
import string
from PIL import Image, ImageDraw


from datetime import timedelta


from http import HTTPStatus
from fastapi.responses import RedirectResponse

from schedula.settings import Settings

settings = Settings()


def obter_conexao():
    return sqlite3.connect(settings.DATABASE_URL)

def criar_toast_cookie(response, toast):
    response.set_cookie(
        key="toast",
        value=json.dumps(toast),
        max_age=1,
        httponly=True,
        samesite="Lax",
    )
    return response

def redirecionar_com_toast(url_destino: str, toast: dict):
    response = RedirectResponse(
        url_destino,
        status_code=HTTPStatus.SEE_OTHER,
    )
    response = criar_toast_cookie(response, toast)
    
    return response

def get_data_dia_semana(dia_semana, referencia_data):
    # Mapeamento dos dias da semana para números (0 = segunda, 6 = domingo)
    dias_da_semana = {
        "SEGUNDA": 0,
        "TERÇA": 1,
        "QUARTA": 2,
        "QUINTA": 3,
        "SEXTA": 4,
        "SÁBADO": 5,
        "DOMINGO": 6
    }

    dia_semana_num = dias_da_semana[dia_semana.upper()]
    start_of_week = referencia_data - timedelta(days=referencia_data.weekday())
    dias_a_ajustar = (dia_semana_num - start_of_week.weekday()) % 7

    data_dia_semana = start_of_week + timedelta(days=dias_a_ajustar)
    
    return data_dia_semana.replace()

def processar_imagem_perfil(imagem) -> bytes:
    """
    Recebe uma imagem no formato de bytes, converte para PNG, aplica um corte redondo de 150px
    e retorna a imagem transformada também em formato de bytes.
    
    :param imagem: Imagem original em formato de bytes.
    :return: Imagem transformada (PNG redonda de 150px) em formato de bytes.
    """
    try:
        # Abrir a imagem recebida
        img = Image.open(io.BytesIO(imagem))

        # Converter para PNG
        img = img.convert("RGBA")

        # Criar uma máscara redonda (circular)
        largura, altura = img.size
        diametro = min(largura, altura)
        mask = Image.new("L", (diametro, diametro), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, diametro, diametro), fill=255)

        # Criar a imagem final com o fundo transparente
        img_circular = Image.new("RGBA", (diametro, diametro), (0, 0, 0, 0))
        img_circular.paste(img.crop((0, 0, diametro, diametro)), (0, 0), mask=mask)

        # Redimensionar para 150px de diâmetro (usando a constante correta)
        img_circular = img_circular.resize((150, 150), Image.Resampling.LANCZOS)

        # Salvar a imagem final em formato PNG em memória
        output = io.BytesIO()
        img_circular.save(output, format="PNG")
        return output.getvalue()
    except:
        return False

def salvar_imagem_em_arquivo(imagem_bytes: bytes, caminho_destino: str):
    """
    Salva a imagem processada em um arquivo no disco.
    
    :param imagem_bytes: A imagem em formato de bytes.
    :param caminho_destino: O caminho completo para onde a imagem será salva (incluindo o nome do arquivo).
    """
    nome_arquivo = _gerar_nome_arquivo()
    path = caminho_destino + nome_arquivo + ".png"

    with open(path, 'wb') as f:
        f.write(imagem_bytes)
    
    return nome_arquivo

def _gerar_nome_arquivo(tamanho: int = 16) -> str:
    """
    Gera um nome aleatório com um número especificado de letras.
    
    :param tamanho: O número de caracteres no nome (padrão é 16).
    :return: Um nome aleatório de letras (maiúsculas e minúsculas).
    """
    return ''.join(random.choices(string.ascii_letters, k=tamanho))