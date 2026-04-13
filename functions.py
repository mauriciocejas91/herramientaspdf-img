import os
import fitz
from PIL import Image, ImageOps
from pypdf import PdfWriter, PdfReader
from pdf2docx import Converter
from docx2pdf import convert as docx_convert
from rembg import remove, new_session

def unir_pdfs(rutas_archivos, ruta_salida):
    try:
        merger = PdfWriter()
        for pdf in rutas_archivos:
            merger.append(pdf)
        
        with open(ruta_salida, "wb") as f:
            merger.write(f)
        merger.close()
        return {"status": "success", "message": f"PDF unido con éxito en:\n{ruta_salida}", "path": ruta_salida}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

def separar_pdf(ruta_archivo, carpeta_salida):
    try:
        reader = PdfReader(ruta_archivo)
        nombre_base = os.path.splitext(os.path.basename(ruta_archivo))[0]
        
        os.makedirs(carpeta_salida, exist_ok=True)
        
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            salida = os.path.join(carpeta_salida, f"{nombre_base}_pagina_{i+1}.pdf")
            with open(salida, "wb") as f:
                writer.write(f)
                
        return {"status": "success", "message": f"Páginas extraídas en:\n{carpeta_salida}", "path": carpeta_salida}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

def pdf_a_word(ruta_pdf, ruta_salida):
    try:
        cv = Converter(ruta_pdf)
        cv.convert(ruta_salida)
        cv.close()
        return {"status": "success", "message": f"Convertido a Word:\n{ruta_salida}", "path": ruta_salida}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

def word_a_pdf(ruta_word, ruta_salida):
    try:
        docx_convert(ruta_word, ruta_salida)
        return {"status": "success", "message": f"Convertido a PDF:\n{ruta_salida}", "path": ruta_salida}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}
    
def comprimir_pdf(ruta_archivo, ruta_salida):
    try:
        reader = PdfReader(ruta_archivo)
        writer = PdfWriter()

        # Agregamos todas las páginas al Writer
        for page in reader.pages:
            writer.add_page(page)
            
        # Ahora que ya son parte del Writer, las comprimimos
        for page in writer.pages:
            page.compress_content_streams()

        with open(ruta_salida, "wb") as f:
            writer.write(f)
            
        # Calculamos el tamaño
        tamano_original = os.path.getsize(ruta_archivo) / (1024 * 1024)
        tamano_nuevo = os.path.getsize(ruta_salida) / (1024 * 1024)
        
        if tamano_original > 0:
            ahorro = ((tamano_original - tamano_nuevo) / tamano_original) * 100
        else:
            ahorro = 0
            
        mensaje = f"PDF Comprimido con éxito.\nDe {tamano_original:.2f} MB a {tamano_nuevo:.2f} MB\n(Ahorraste un {ahorro:.1f}%)"

        return {"status": "success", "message": mensaje, "path": ruta_salida}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

def pdf_a_imagen(ruta_pdf, carpeta_salida, formato="jpg"):
    try:
        doc = fitz.open(ruta_pdf)
        nombre_base = os.path.splitext(os.path.basename(ruta_pdf))[0]
        
        os.makedirs(carpeta_salida, exist_ok=True)
        
        for i in range(len(doc)):
            pagina = doc.load_page(i)
            # dpi=300 asegura una alta calidad de imagen
            pix = pagina.get_pixmap(dpi=300) 
            salida = os.path.join(carpeta_salida, f"{nombre_base}_pagina_{i+1}.{formato}")
            pix.save(salida)
            
        doc.close()
        return {"status": "success", "message": f"Imágenes extraídas en:\n{carpeta_salida}", "path": carpeta_salida}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}
    
# FUNCIONES IMAGENES

def comprimir_imagen(ruta_imagen, ruta_salida, calidad=60):
    try:
        img = Image.open(ruta_imagen)
        
        # Si la imagen es RGBA (con transparencia) y se guardará como JPG, hay que convertirla a RGB
        if img.mode in ("RGBA", "P") and ruta_salida.lower().endswith(('.jpg', '.jpeg')):
            img = img.convert("RGB")
            
        # PNG usa un algoritmo distinto (optimize), JPG/WEBP usan 'quality'
        if img.format == 'PNG' or ruta_salida.lower().endswith('.png'):
            img.save(ruta_salida, optimize=True)
        else:
            img.save(ruta_salida, quality=calidad, optimize=True)
            
        # Calculamos el tamaño
        tamano_original = os.path.getsize(ruta_imagen) / (1024 * 1024)
        tamano_nuevo = os.path.getsize(ruta_salida) / (1024 * 1024)
        
        if tamano_original > 0:
            ahorro = ((tamano_original - tamano_nuevo) / tamano_original) * 100
        else:
            ahorro = 0
            
        mensaje = f"Imagen comprimida.\nDe {tamano_original:.2f} MB a {tamano_nuevo:.2f} MB\n(Ahorraste un {ahorro:.1f}%)"

        return {"status": "success", "message": mensaje, "path": ruta_salida}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

def quitar_fondo(ruta_imagen, ruta_salida):
    try:
        input_image = Image.open(ruta_imagen)
        
        # Iniciamos una sesión con un modelo de alta calidad.
        # "isnet-general-use" es excelente para e-commerce y objetos.
        # Otra opción muy potente es "briarmbg1.4" si tienes rembg actualizado.
        sesion_ia = new_session("isnet-general-use")
        
        # Le pasamos la sesión a la función remove
        output_image = remove(input_image, session=sesion_ia)
        
        output_image.save(ruta_salida, format="PNG")
        
        mensaje = f"Fondo eliminado (Alta Calidad).\nGuardado en:\n{ruta_salida}"
        return {"status": "success", "message": mensaje, "path": ruta_salida}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}
    
def recortar_interactivo(ruta_imagen, ruta_salida, x, y, width, height):
    try:
        img = Image.open(ruta_imagen)
        img = ImageOps.exif_transpose(img)
        
        # Pillow crop usa una tupla: (izquierda, superior, derecha, inferior)
        left = int(x)
        upper = int(y)
        right = int(x + width)
        lower = int(y + height)

        img_recortada = img.crop((left, upper, right, lower))

        formato = img.format if img.format else "JPEG"
        if ruta_salida.lower().endswith('.png'):
            formato = "PNG"
            
        img_recortada.save(ruta_salida, format=formato, optimize=True)
        
        mensaje = f"Imagen recortada.\nGuardado en:\n{ruta_salida}"
        return {"status": "success", "message": mensaje, "path": ruta_salida}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}