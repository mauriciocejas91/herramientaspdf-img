import os
import fitz
from PIL import Image, ImageOps, ImageDraw, ImageFont
from pypdf import PdfWriter, PdfReader
from pdf2docx import Converter
from docx2pdf import convert as docx_convert
from rembg import remove, new_session

def unir_pdfs(rutas_archivos, ruta_salida):
    try:
        merger = PdfWriter()
        for pdf in rutas_archivos: merger.append(pdf)
        with open(ruta_salida, "wb") as f: merger.write(f)
        merger.close()
        return {"status": "success", "message": f"PDF unido con éxito en:\n{ruta_salida}", "path": ruta_salida}
    except Exception as e: return {"status": "error", "message": f"Error: {str(e)}"}

def separar_pdf(ruta_archivo, carpeta_salida):
    try:
        reader = PdfReader(ruta_archivo)
        nombre_base = os.path.splitext(os.path.basename(ruta_archivo))[0]
        os.makedirs(carpeta_salida, exist_ok=True)
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            salida = os.path.join(carpeta_salida, f"{nombre_base}_pagina_{i+1}.pdf")
            with open(salida, "wb") as f: writer.write(f)
        return {"status": "success", "message": f"Páginas extraídas en:\n{carpeta_salida}", "path": carpeta_salida}
    except Exception as e: return {"status": "error", "message": f"Error: {str(e)}"}

def pdf_a_word(ruta_pdf, ruta_salida):
    try:
        cv = Converter(ruta_pdf)
        cv.convert(ruta_salida)
        cv.close()
        return {"status": "success", "message": f"Convertido a Word:\n{ruta_salida}", "path": ruta_salida}
    except Exception as e: return {"status": "error", "message": f"Error: {str(e)}"}

def word_a_pdf(ruta_word, ruta_salida):
    try:
        docx_convert(ruta_word, ruta_salida)
        return {"status": "success", "message": f"Convertido a PDF:\n{ruta_salida}", "path": ruta_salida}
    except Exception as e: return {"status": "error", "message": f"Error: {str(e)}"}
    
def comprimir_pdf(ruta_archivo, ruta_salida):
    try:
        reader = PdfReader(ruta_archivo)
        writer = PdfWriter()
        for page in reader.pages: writer.add_page(page)
        for page in writer.pages: page.compress_content_streams()
        with open(ruta_salida, "wb") as f: writer.write(f)
        tamano_original = os.path.getsize(ruta_archivo) / (1024 * 1024)
        tamano_nuevo = os.path.getsize(ruta_salida) / (1024 * 1024)
        ahorro = ((tamano_original - tamano_nuevo) / tamano_original) * 100 if tamano_original > 0 else 0
        mensaje = f"PDF Comprimido con éxito.\nDe {tamano_original:.2f} MB a {tamano_nuevo:.2f} MB\n(Ahorraste un {ahorro:.1f}%)"
        return {"status": "success", "message": mensaje, "path": ruta_salida}
    except Exception as e: return {"status": "error", "message": f"Error: {str(e)}"}

def pdf_a_imagen(ruta_pdf, carpeta_salida, formato="jpg"):
    try:
        doc = fitz.open(ruta_pdf)
        nombre_base = os.path.splitext(os.path.basename(ruta_pdf))[0]
        os.makedirs(carpeta_salida, exist_ok=True)
        for i in range(len(doc)):
            pagina = doc.load_page(i)
            pix = pagina.get_pixmap(dpi=300) 
            salida = os.path.join(carpeta_salida, f"{nombre_base}_pagina_{i+1}.{formato}")
            pix.save(salida)
        doc.close()
        return {"status": "success", "message": f"Imágenes extraídas en:\n{carpeta_salida}", "path": carpeta_salida}
    except Exception as e: return {"status": "error", "message": f"Error: {str(e)}"}

def comprimir_imagen(ruta_imagen, ruta_salida, calidad=60):
    try:
        img = Image.open(ruta_imagen)
        if img.mode in ("RGBA", "P") and ruta_salida.lower().endswith(('.jpg', '.jpeg')): img = img.convert("RGB")
        if img.format == 'PNG' or ruta_salida.lower().endswith('.png'): img.save(ruta_salida, optimize=True)
        else: img.save(ruta_salida, quality=calidad, optimize=True)
        tamano_original = os.path.getsize(ruta_imagen) / (1024 * 1024)
        tamano_nuevo = os.path.getsize(ruta_salida) / (1024 * 1024)
        ahorro = ((tamano_original - tamano_nuevo) / tamano_original) * 100 if tamano_original > 0 else 0
        mensaje = f"Imagen comprimida.\nDe {tamano_original:.2f} MB a {tamano_nuevo:.2f} MB\n(Ahorraste un {ahorro:.1f}%)"
        return {"status": "success", "message": mensaje, "path": ruta_salida}
    except Exception as e: return {"status": "error", "message": f"Error: {str(e)}"}

def quitar_fondo(ruta_imagen, ruta_salida):
    try:
        input_image = Image.open(ruta_imagen)
        sesion_ia = new_session("isnet-general-use")
        output_image = remove(input_image, session=sesion_ia)
        output_image.save(ruta_salida, format="PNG")
        return {"status": "success", "message": f"Fondo eliminado.\nGuardado en:\n{ruta_salida}", "path": ruta_salida}
    except Exception as e: return {"status": "error", "message": f"Error: {str(e)}"}
    
def recortar_interactivo(ruta_imagen, ruta_salida, x, y, width, height):
    try:
        img = Image.open(ruta_imagen)
        img = ImageOps.exif_transpose(img)
        left, upper, right, lower = int(x), int(y), int(x + width), int(y + height)
        img_recortada = img.crop((left, upper, right, lower))
        formato = "PNG" if ruta_salida.lower().endswith('.png') else (img.format if img.format else "JPEG")
        img_recortada.save(ruta_salida, format=formato, optimize=True)
        return {"status": "success", "message": f"Imagen recortada.\nGuardado en:\n{ruta_salida}", "path": ruta_salida}
    except Exception as e: return {"status": "error", "message": f"Error: {str(e)}"}

def agregar_marca_agua_texto(ruta_imagen, ruta_salida, texto, color, fuente_nombre, posicion):
    try:
        img = Image.open(ruta_imagen)
        if img.mode != 'RGBA': img = img.convert('RGBA')

        d = ImageDraw.Draw(img)
        font_size = max(15, int(img.width * 0.05))
        try:
            fuentes = {"arial": "arial.ttf", "times": "times.ttf", "courier": "cour.ttf"}
            font = ImageFont.truetype(fuentes.get(fuente_nombre, "arial.ttf"), font_size)
        except IOError:
            font = ImageFont.load_default()

        bbox = d.textbbox((0, 0), texto, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        padding = 20
        x, y = 0, 0
        
        if posicion == "bottom-right": x, y = img.width - text_width - padding, img.height - text_height - padding
        elif posicion == "bottom-left": x, y = padding, img.height - text_height - padding
        elif posicion == "top-right": x, y = img.width - text_width - padding, padding
        elif posicion == "top-left": x, y = padding, padding
        elif posicion == "center": x, y = (img.width - text_width) // 2, (img.height - text_height) // 2

        color_hex = color.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        d.text((x, y), texto, fill=(r, g, b, 200), font=font)

        formato_salida = os.path.splitext(ruta_salida)[1].lower()
        if formato_salida in ['.jpg', '.jpeg']:
            img = img.convert("RGB")
            img.save(ruta_salida, quality=90)
        else:
            img.save(ruta_salida)

        return {"status": "success", "message": f"Firma añadida con éxito.\nGuardado en:\n{ruta_salida}", "path": ruta_salida}
    except Exception as e: return {"status": "error", "message": f"Error al procesar: {str(e)}"}

def agregar_marca_agua_imagen(ruta_imagen, ruta_salida, ruta_logo, posicion):
    try:
        img = Image.open(ruta_imagen)
        if img.mode != 'RGBA': img = img.convert('RGBA')
            
        logo = Image.open(ruta_logo)
        if logo.mode != 'RGBA': logo = logo.convert('RGBA')
            
        ancho_base = int(img.width * 0.15)
        if ancho_base < 50: ancho_base = 50 
            
        proporcion = (ancho_base / float(logo.width))
        alto_nuevo = int((float(logo.height) * float(proporcion)))
        
        try: filtro = Image.Resampling.LANCZOS
        except AttributeError: filtro = Image.LANCZOS

        logo = logo.resize((ancho_base, alto_nuevo), filtro)
        
        padding = 20
        x, y = 0, 0
        
        if posicion == "bottom-right": x, y = img.width - logo.width - padding, img.height - logo.height - padding
        elif posicion == "bottom-left": x, y = padding, img.height - logo.height - padding
        elif posicion == "top-right": x, y = img.width - logo.width - padding, padding
        elif posicion == "top-left": x, y = padding, padding
        elif posicion == "center": x, y = (img.width - logo.width) // 2, (img.height - logo.height) // 2
            
        img.paste(logo, (x, y), logo)
        
        formato_salida = os.path.splitext(ruta_salida)[1].lower()
        if formato_salida in ['.jpg', '.jpeg']:
            img = img.convert("RGB")
            img.save(ruta_salida, quality=90)
        else:
            img.save(ruta_salida)

        return {"status": "success", "message": f"Logo añadido con éxito.\nGuardado en:\n{ruta_salida}", "path": ruta_salida}
    except Exception as e: return {"status": "error", "message": f"Error al procesar logo: {str(e)}"}