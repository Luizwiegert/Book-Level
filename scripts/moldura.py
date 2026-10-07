"""Coloca os screenshots do app numa moldura de celular.

Uso: python scripts/moldura.py
Lê docs/screenshots/tela-*.png e grava docs/screenshots/celular-*.png
e docs/screenshots/celulares.png (as telas lado a lado). Dependência: Pillow.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DIR = Path(__file__).resolve().parent.parent / "docs" / "screenshots"
TELAS = ["inicio", "livros", "progresso", "perfil"]

BORDA = 26          # espessura da moldura
RAIO_TELA = 96      # canto da tela
AA = 3              # supersampling das formas


def rounded(size, radius, fill):
    w, h = size
    big = Image.new("L", (w * AA, h * AA), 0)
    ImageDraw.Draw(big).rounded_rectangle((0, 0, w * AA - 1, h * AA - 1), radius * AA, fill=255)
    layer = Image.new("RGBA", size, fill)
    layer.putalpha(big.resize(size, Image.LANCZOS))
    return layer


def barra_de_status(tela):
    """Desenha hora, sinal e bateria na faixa livre do topo do app."""
    sw, _ = tela.size
    r, g, b = tela.getpixel((sw // 2, 20))[:3]
    cor = (20, 24, 32, 255) if (r + g + b) / 3 > 128 else (255, 255, 255, 255)
    d = ImageDraw.Draw(tela)
    try:
        fonte = ImageFont.truetype("arialbd.ttf", 30)
    except OSError:
        fonte = ImageFont.load_default()
    d.text((92, 40), "9:41", font=fonte, fill=cor)
    for i in range(4):
        d.rounded_rectangle((sw - 214 + i * 13, 68 - 7 * (i + 1), sw - 206 + i * 13, 70), 2, fill=cor)
    d.rounded_rectangle((sw - 140, 44, sw - 88, 70), 7, outline=cor[:3] + (140,), width=2)
    d.rounded_rectangle((sw - 136, 48, sw - 98, 66), 4, fill=cor)
    return tela


def emoldurar(tela):
    tela = barra_de_status(tela.convert("RGBA"))
    sw, sh = tela.size
    lado = 6  # sobra lateral para os botões
    w, h = sw + 2 * BORDA + 2 * lado, sh + 2 * BORDA
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    botoes = ImageDraw.Draw(out)
    cor_botao = (58, 58, 64, 255)
    botoes.rounded_rectangle((0, 300, lado + 4, 370), 3, fill=cor_botao)
    botoes.rounded_rectangle((0, 430, lado + 4, 560), 3, fill=cor_botao)
    botoes.rounded_rectangle((0, 590, lado + 4, 720), 3, fill=cor_botao)
    botoes.rounded_rectangle((w - lado - 4, 480, w, 690), 3, fill=cor_botao)

    out.alpha_composite(rounded((sw + 2 * BORDA, h), RAIO_TELA + BORDA, (72, 72, 80, 255)), (lado, 0))
    out.alpha_composite(rounded((sw + 2 * BORDA - 8, h - 8), RAIO_TELA + BORDA - 4, (12, 12, 14, 255)), (lado + 4, 4))

    tela.putalpha(rounded((sw, sh), RAIO_TELA, (0, 0, 0, 255)).getchannel("A"))
    out.alpha_composite(tela, (lado + BORDA, BORDA))

    iw, ih = 216, 60
    out.alpha_composite(rounded((iw, ih), ih // 2, (0, 0, 0, 255)), ((w - iw) // 2, BORDA + 22))
    return out


def main():
    prontos = []
    for nome in TELAS:
        img = emoldurar(Image.open(DIR / f"tela-{nome}.png"))
        img.save(DIR / f"celular-{nome}.png", optimize=True)
        prontos.append(img)

    gap = 90
    w = sum(i.width for i in prontos) + gap * (len(prontos) - 1)
    h = max(i.height for i in prontos)
    todos = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for img in prontos:
        todos.alpha_composite(img, (x, 0))
        x += img.width + gap
    todos = todos.resize((2200, round(h * 2200 / w)), Image.LANCZOS)
    todos.save(DIR / "celulares.png", optimize=True)
    print(todos.size)


if __name__ == "__main__":
    main()
