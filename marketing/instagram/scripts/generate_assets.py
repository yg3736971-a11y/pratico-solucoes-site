#!/usr/bin/env python3
"""Gera o kit inicial do Instagram da Prático Soluções."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
EXPORT = ROOT / "export"

GREEN = "#092F2B"
GREEN_DEEP = "#052420"
GREEN_SOFT = "#16433E"
ORANGE = "#FF8A34"
ORANGE_BRIGHT = "#FF9F58"
CREAM = "#F7F3EA"
SAND = "#E8DFD0"
WHITE = "#FFFFFF"
TEXT = "#18342F"
MUTED = "#667772"
WHATSAPP = "(11) 96526-7558"

FONTS = {
    "display": SOURCE / "fonts" / "Sora-Bold.ttf",
    "body": SOURCE / "fonts" / "Manrope-Regular.ttf",
    "semibold": SOURCE / "fonts" / "Manrope-SemiBold.ttf",
    "bold": SOURCE / "fonts" / "Manrope-Bold.ttf",
    "extra": SOURCE / "fonts" / "Manrope-ExtraBold.ttf",
}


def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS[kind]), size)


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def gradient(size: tuple[int, int], start: str, end: str) -> Image.Image:
    w, h = min(size[0], 256), min(size[1], 256)
    image = Image.new("RGB", (w, h))
    px = image.load()
    a, b = rgb(start), rgb(end)
    for y in range(h):
        for x in range(w):
            t = (x + y) / max(1, w + h - 2)
            px[x, y] = tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))
    return image.resize(size, Image.Resampling.BICUBIC)


def fit(path: Path, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(Image.open(path).convert("RGB"), size, method=Image.Resampling.LANCZOS)


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(path, "PNG", optimize=True)


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=face)[2] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, face: ImageFont.FreeTypeFont, fill: str, width: int, gap: int = 12) -> int:
    x, y = xy
    for line in wrap(draw, text, face, width):
        draw.text((x, y), line, font=face, fill=fill)
        box = draw.textbbox((x, y), line, font=face)
        y += box[3] - box[1] + gap
    return y


def logo(image: Image.Image, x: int, y: int, *, light: bool, scale: float = 1.0) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    box = int(76 * scale)
    draw.rounded_rectangle((x, y, x + box, y + box), radius=int(15 * scale), fill=ORANGE)
    draw.rectangle((x + int(20 * scale), y + int(16 * scale), x + int(33 * scale), y + int(60 * scale)), fill=GREEN)
    draw.rounded_rectangle((x + int(27 * scale), y + int(16 * scale), x + int(58 * scale), y + int(43 * scale)), radius=int(9 * scale), outline=GREEN, width=max(3, int(9 * scale)))
    color = WHITE if light else GREEN
    draw.text((x + box + int(16 * scale), y - int(6 * scale)), "Prático", font=font("extra", int(40 * scale)), fill=color)
    draw.text((x + box + int(17 * scale), y + int(39 * scale)), "SOLUÇÕES", font=font("bold", int(17 * scale)), fill=ORANGE)
    image.alpha_composite(layer)


def whatsapp_badge(image: Image.Image, y: int, *, centered: bool = False) -> None:
    draw = ImageDraw.Draw(image)
    width, height = 560, 76
    x = (image.width - width) // 2 if centered else 64
    draw.rounded_rectangle((x, y, x + width, y + height), radius=38, fill="#1F9D63")
    draw.ellipse((x + 24, y + 19, x + 62, y + 57), outline=WHITE, width=4)
    draw.text((x + 83, y + 19), f"WhatsApp {WHATSAPP}", font=font("bold", 28), fill=WHITE)


def photo_post(title: str, subtitle: str, tag: str, photo: Path, output: Path, *, whatsapp: bool = False) -> None:
    size = (1080, 1350)
    image = fit(photo, size).convert("RGBA")
    image = ImageEnhance.Brightness(image).enhance(0.82)
    shade = Image.new("RGBA", size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rectangle((0, 0, 1080, 550), fill=(5, 36, 32, 195))
    sd.rectangle((0, 1010, 1080, 1350), fill=(5, 36, 32, 165))
    image.alpha_composite(shade.filter(ImageFilter.GaussianBlur(10)))
    draw = ImageDraw.Draw(image)
    logo(image, 64, 52, light=True, scale=0.88)
    draw.rounded_rectangle((64, 205, 440, 258), radius=26, fill=ORANGE)
    draw.text((90, 218), tag.upper(), font=font("bold", 20), fill=GREEN)
    y = wrapped(draw, (64, 306), title, font("display", 64), WHITE, 900, 10)
    wrapped(draw, (64, y + 24), subtitle, font("body", 31), "#F7F3EA", 820, 12)
    if whatsapp:
        whatsapp_badge(image, 1175)
    else:
        draw.text((64, 1260), "Atendimento na região central de São Paulo", font=font("semibold", 23), fill="#F7F3EA")
    save(image, output)


def graphic_post(title: str, subtitle: str, tag: str, output: Path, *, whatsapp: bool = False, dark: bool = False) -> None:
    size = (1080, 1350)
    image = gradient(size, GREEN_DEEP if dark else CREAM, GREEN_SOFT if dark else "#FFFDF8").convert("RGBA")
    draw = ImageDraw.Draw(image)
    logo(image, 64, 52, light=dark, scale=0.88)
    draw.rounded_rectangle((64, 220, 430, 274), radius=27, fill=ORANGE)
    draw.text((90, 233), tag.upper(), font=font("bold", 20), fill=GREEN)
    y = wrapped(draw, (64, 355), title, font("display", 70), WHITE if dark else GREEN, 900, 14)
    wrapped(draw, (64, y + 34), subtitle, font("body", 33), "#E8DFD0" if dark else TEXT, 830, 14)
    draw.ellipse((750, 840, 1120, 1210), fill=rgb(ORANGE) + (46 if dark else 70,))
    draw.line((64, 1185, 1016, 1185), fill=ORANGE, width=3)
    if whatsapp:
        whatsapp_badge(image, 1220)
    else:
        draw.text((64, 1230), "Residências • Condomínios • Empresas", font=font("semibold", 24), fill=ORANGE if dark else GREEN_SOFT)
    save(image, output)


def service_grid(output: Path) -> None:
    size = (1080, 1350)
    image = gradient(size, CREAM, "#FFFDF8").convert("RGBA")
    draw = ImageDraw.Draw(image)
    logo(image, 64, 52, light=False, scale=0.88)
    draw.text((64, 230), "UMA EQUIPE. VÁRIAS SOLUÇÕES.", font=font("bold", 22), fill=ORANGE)
    wrapped(draw, (64, 300), "O serviço certo para cada necessidade.", font("display", 60), GREEN, 900, 12)
    services = ["Serralheria", "Elétrica", "Marido de aluguel", "Manutenção predial", "Reparos", "Outras instalações"]
    for idx, service in enumerate(services):
        col, row = idx % 2, idx // 2
        x, y = 64 + col * 480, 590 + row * 170
        draw.rounded_rectangle((x, y, x + 435, y + 130), radius=24, fill=WHITE, outline="#D7CCBA", width=2)
        draw.ellipse((x + 25, y + 34, x + 87, y + 96), fill=ORANGE)
        draw.text((x + 112, y + 47), service, font=font("bold", 25), fill=GREEN)
    draw.text((64, 1230), "Atendimento na região central de São Paulo", font=font("semibold", 24), fill=MUTED)
    save(image, output)


def story(title: str, subtitle: str, output: Path, photo: Path | None = None, *, whatsapp: bool = False, sticker: str = "") -> None:
    size = (1080, 1920)
    image = (fit(photo, size) if photo else gradient(size, GREEN_DEEP, GREEN_SOFT)).convert("RGBA")
    if photo:
        image = ImageEnhance.Brightness(image).enhance(0.68)
    overlay = Image.new("RGBA", size, (5, 36, 32, 75))
    image.alpha_composite(overlay)
    draw = ImageDraw.Draw(image)
    logo(image, 70, 90, light=True, scale=1.0)
    y = wrapped(draw, (70, 540), title, font("display", 80), WHITE, 920, 18)
    wrapped(draw, (70, y + 38), subtitle, font("body", 39), CREAM, 860, 18)
    if whatsapp:
        whatsapp_badge(image, 1560, centered=True)
    elif sticker:
        draw.rounded_rectangle((70, 1540, 1010, 1680), radius=42, fill=(247, 243, 234, 245))
        draw.text((115, 1582), sticker, font=font("bold", 32), fill=GREEN)
    draw.text((70, 1800), "Prático Soluções • Centro de São Paulo", font=font("semibold", 27), fill="#F7F3EA")
    save(image, output)


def reel(title: str, output: Path, photo: Path, number: str) -> None:
    size = (1080, 1920)
    image = fit(photo, size).convert("RGBA")
    image = ImageEnhance.Brightness(image).enhance(0.62)
    image.alpha_composite(Image.new("RGBA", size, (5, 36, 32, 85)))
    draw = ImageDraw.Draw(image)
    logo(image, 70, 80, light=True)
    draw.rounded_rectangle((70, 410, 350, 470), radius=30, fill=ORANGE)
    draw.text((105, 425), f"REEL {number}", font=font("bold", 24), fill=GREEN)
    wrapped(draw, (70, 560), title, font("display", 82), WHITE, 900, 20)
    draw.rounded_rectangle((70, 1610, 430, 1700), radius=45, fill=ORANGE)
    draw.text((122, 1634), "ASSISTA →", font=font("extra", 31), fill=GREEN)
    save(image, output)


def highlight(label: str, output: Path, index: int) -> None:
    size = (1080, 1080)
    image = gradient(size, GREEN_DEEP, GREEN_SOFT).convert("RGBA")
    draw = ImageDraw.Draw(image)
    draw.ellipse((235, 155, 845, 765), fill=ORANGE, outline=CREAM, width=10)
    # Ferramenta abstrata e segura para miniatura circular.
    draw.rounded_rectangle((450, 290, 565, 615), radius=44, fill=GREEN)
    draw.ellipse((418, 255, 595, 430), outline=GREEN, width=30)
    draw.line((500, 560, 650, 700), fill=GREEN, width=34)
    bbox = draw.textbbox((0, 0), label.upper(), font=font("extra", 31))
    draw.text(((1080 - (bbox[2] - bbox[0])) // 2, 835), label.upper(), font=font("extra", 31), fill=WHITE)
    save(image, output)


def carousel_slide(number: str, title: str, body: str, output: Path, *, whatsapp: bool = False) -> None:
    size = (1080, 1350)
    image = gradient(size, CREAM, "#FFFDF8").convert("RGBA")
    draw = ImageDraw.Draw(image)
    logo(image, 64, 52, light=False, scale=0.88)
    draw.text((64, 240), number, font=font("display", 48), fill=ORANGE)
    y = wrapped(draw, (64, 390), title, font("display", 68), GREEN, 900, 14)
    wrapped(draw, (64, y + 34), body, font("body", 35), TEXT, 830, 16)
    if whatsapp:
        whatsapp_badge(image, 1060)
    draw.text((910, 1250), f"{number}/04", font=font("bold", 23), fill=MUTED)
    save(image, output)


def contact_sheet(paths: Iterable[Path], output: Path) -> None:
    paths = list(paths)
    thumb = (300, 375)
    cols = 3
    sheet = Image.new("RGB", (900, math.ceil(len(paths) / cols) * 375), rgb(GREEN_DEEP))
    for idx, path in enumerate(paths):
        image = ImageOps.fit(Image.open(path).convert("RGB"), thumb, Image.Resampling.LANCZOS)
        sheet.paste(image, ((idx % cols) * 300, (idx // cols) * 375))
    save(sheet.convert("RGBA"), output)


def avatar(output: Path) -> None:
    image = Image.new("RGBA", (1080, 1080), rgb(ORANGE) + (255,))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((225, 195, 855, 825), radius=130, fill=GREEN)
    draw.rectangle((390, 315, 495, 705), fill=ORANGE)
    draw.rounded_rectangle((455, 315, 710, 550), radius=75, outline=ORANGE, width=70)
    save(image, output)


def main() -> None:
    photos = SOURCE / "photos"
    feed = EXPORT / "feed"

    photo_post("Seu espaço funcionando do jeito certo.", "Serviços e manutenção para residências, condomínios e empresas.", "Prático Soluções", photos / "predial.png", feed / "01-apresentacao.png", whatsapp=True)
    service_grid(feed / "02-servicos.png")
    photo_post("Serralheria com avaliação profissional.", "Reparos, ajustes, soldas, portões, grades, corrimãos e estruturas metálicas.", "Serralheria", photos / "serralheria.png", feed / "03-serralheria.png")
    photo_post("Elétrica: instalação e manutenção.", "Tomadas, iluminação, quadros, disjuntores e correções elétricas.", "Elétrica", photos / "eletrica.png", feed / "04-eletrica.png")
    photo_post("Os pequenos serviços que fazem diferença.", "Montagens, fixações, trocas e ajustes do dia a dia.", "Marido de aluguel", photos / "marido-aluguel.png", feed / "05-marido-de-aluguel.png")
    photo_post("Manutenção predial organizada.", "Atendimento corretivo e preventivo para condomínios, comércios e empresas.", "Manutenção predial", photos / "predial.png", feed / "06-manutencao-predial.png")
    photo_post("Reparar agora evita transtorno depois.", "Avaliação de problemas, correções e ajustes em diferentes áreas do imóvel.", "Reparos", photos / "reparos.png", feed / "07-reparos.png")
    graphic_post("Como pedir uma avaliação?", "Envie o serviço, tipo de imóvel, bairro e fotos quando possível. A equipe confirma cobertura, disponibilidade e próximos passos.", "Pedido organizado", feed / "08-como-pedir-orcamento.png", whatsapp=True)
    graphic_post("Residências, condomínios e empresas.", "Uma equipe para cuidar de reparos, instalações e manutenções do seu imóvel.", "Quem atendemos", feed / "09-publicos.png")
    photo_post("Atendimento na região central de São Paulo.", "Envie seu bairro para a equipe confirmar a cobertura e a disponibilidade.", "Área de atendimento", photos / "predial.png", feed / "10-regiao-central.png", whatsapp=True)
    graphic_post("Posso enviar fotos pelo WhatsApp?", "Sim. Fotos do local ou do item ajudam na avaliação. Evite mostrar documentos ou informações privadas.", "Dúvida frequente", feed / "11-envio-de-fotos.png")
    graphic_post("Conte o que precisa. A gente organiza o atendimento.", "Preço, prazo, cobertura e agenda são confirmados por uma pessoa depois da avaliação do pedido.", "Solicite uma avaliação", feed / "12-cta-whatsapp.png", whatsapp=True, dark=True)

    carousel_slide("01", "Escolha o serviço.", "Serralheria, elétrica, marido de aluguel, manutenção predial, reparos ou outra instalação.", EXPORT / "carousel-01" / "01-servico.png")
    carousel_slide("02", "Informe o tipo de imóvel.", "Residência, apartamento, condomínio, comércio ou empresa.", EXPORT / "carousel-01" / "02-imovel.png")
    carousel_slide("03", "Envie o bairro e uma descrição.", "Fotos podem ajudar a equipe a entender melhor a necessidade.", EXPORT / "carousel-01" / "03-detalhes.png")
    carousel_slide("04", "Receba a confirmação humana.", "A equipe confirma cobertura, disponibilidade, avaliação e próximos passos.", EXPORT / "carousel-01" / "04-confirmacao.png", whatsapp=True)

    stories = [
        ("O que precisa ser resolvido hoje?", "Escolha o serviço e conte sua necessidade.", photos / "reparos.png", False, "CAIXA DE PERGUNTAS"),
        ("Portão, grade ou estrutura metálica?", "A Prático Soluções realiza avaliação de serviços de serralheria.", photos / "serralheria.png", True, ""),
        ("Tomada, iluminação ou quadro elétrico?", "Envie uma descrição e, quando possível, fotos do local.", photos / "eletrica.png", True, ""),
        ("Tem pequenos reparos acumulados?", "Montagens, fixações, trocas e ajustes do dia a dia.", photos / "marido-aluguel.png", False, "ENQUETE: Sim / Alguns"),
        ("Manutenção para condomínio ou empresa.", "Solicitações corretivas e preventivas na região central de São Paulo.", photos / "predial.png", True, ""),
        ("Fotos ajudam na avaliação.", "Evite mostrar documentos, pessoas ou informações privadas sem necessidade.", photos / "reparos.png", False, "SALVAR"),
        ("Atendimento na região central de São Paulo.", "Envie seu bairro para confirmar a cobertura.", photos / "predial.png", True, ""),
        ("Seu espaço funcionando do jeito certo.", "Prático Soluções para residências, condomínios e empresas.", photos / "predial.png", True, ""),
    ]
    for idx, (title, subtitle, photo, use_whatsapp, sticker) in enumerate(stories, 1):
        story(title, subtitle, EXPORT / "stories" / f"{idx:02d}.png", photo, whatsapp=use_whatsapp, sticker=sticker)

    reel("3 reparos que não devem ficar para depois", EXPORT / "reels" / "01-reparos.png", photos / "reparos.png", "01")
    reel("Quando chamar um profissional de elétrica?", EXPORT / "reels" / "02-eletrica.png", photos / "eletrica.png", "02")
    reel("Como funciona o pedido de avaliação", EXPORT / "reels" / "03-orcamento.png", photos / "predial.png", "03")
    reel("Serralheria: do ajuste à correção", EXPORT / "reels" / "04-serralheria.png", photos / "serralheria.png", "04")

    for idx, label in enumerate(["Serviços", "Serralheria", "Elétrica", "Reparos", "Predial", "Orçamento", "Região"], 1):
        highlight(label, EXPORT / "profile" / "highlights" / f"{idx:02d}-{label.lower()}.png", idx)
    avatar(EXPORT / "profile" / "avatar.png")
    contact_sheet(sorted(feed.glob("*.png")), EXPORT / "preview-grid.png")

    manifest = {
        "client": "Prático Soluções",
        "whatsapp": "5511965267558",
        "service_area": "Região central de São Paulo",
        "exports": {"feed": 12, "carousel": 4, "stories": 8, "reels": 4, "highlights": 7, "avatar": 1},
    }
    (EXPORT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
