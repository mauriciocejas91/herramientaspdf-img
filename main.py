import webview
import os
import platform
import subprocess
import json
import base64
from functions import unir_pdfs, separar_pdf, pdf_a_word, word_a_pdf, comprimir_pdf, pdf_a_imagen, comprimir_imagen, quitar_fondo, recortar_interactivo, agregar_marca_agua_texto, agregar_marca_agua_imagen
from webview.dom import DOMEventHandler

class API:
    def seleccionar_archivos(self, multiple=True, tipo="pdf"):
        if tipo == "word":
            tipos_permitidos = ('Archivos Word (*.docx)',)
        elif tipo == "img":
            tipos_permitidos = ('Imágenes (*.png;*.jpg;*.jpeg;*.webp;*.avif)',)
        else:
            tipos_permitidos = ('Archivos PDF (*.pdf)',)
            
        files = window.create_file_dialog(webview.FileDialog.OPEN, allow_multiple=multiple, file_types=tipos_permitidos)
        return files if files else []

    def ejecutar_unir(self, rutas):
        if len(rutas) < 2:
            return {"status": "error", "message": "Se necesitan al menos 2 archivos."}
        output_path = os.path.join(os.path.dirname(rutas[0]), "PDF_Unido.pdf")
        return unir_pdfs(rutas, output_path)

    def ejecutar_separar(self, rutas):
        if not rutas:
            return {"status": "error", "message": "No hay archivo seleccionado."}
        carpeta_salida = os.path.join(os.path.dirname(rutas[0]), "PDF_Separados")
        return separar_pdf(rutas[0], carpeta_salida)

    def ejecutar_pdf_word(self, rutas):
        if not rutas:
            return {"status": "error", "message": "No hay archivo seleccionado."}
        nombre_base = os.path.splitext(rutas[0])[0]
        output_path = f"{nombre_base}.docx"
        return pdf_a_word(rutas[0], output_path)

    def ejecutar_word_pdf(self, rutas):
        if not rutas:
            return {"status": "error", "message": "No hay archivo seleccionado."}
        nombre_base = os.path.splitext(rutas[0])[0]
        output_path = f"{nombre_base}.pdf"
        return word_a_pdf(rutas[0], output_path)

    def ejecutar_comprimir(self, rutas):
        if not rutas:
            return {"status": "error", "message": "No hay archivo seleccionado."}
        nombre_base = os.path.splitext(rutas[0])[0]
        output_path = f"{nombre_base}_comprimido.pdf"
        return comprimir_pdf(rutas[0], output_path)

    def abrir_archivo(self, ruta):
        if not ruta or not os.path.exists(ruta): return
        if platform.system() == 'Windows':
            os.startfile(ruta)
        elif platform.system() == 'Darwin':
            subprocess.call(['open', ruta])
        else:
            subprocess.call(['xdg-open', ruta])

    def abrir_carpeta(self, ruta):
        if not ruta or not os.path.exists(ruta): return
        carpeta = ruta if os.path.isdir(ruta) else os.path.dirname(ruta)
        if platform.system() == 'Windows':
            os.startfile(carpeta)
        elif platform.system() == 'Darwin':
            subprocess.call(['open', carpeta])
        else:
            subprocess.call(['xdg-open', carpeta])
    
    def ejecutar_pdf_imagen(self, rutas, formato):
        if not rutas:
            return {"status": "error", "message": "No hay archivo seleccionado."}
        carpeta_salida = os.path.join(os.path.dirname(rutas[0]), f"PDF_a_{formato.upper()}")
        return pdf_a_imagen(rutas[0], carpeta_salida, formato)
    
    # FUNCIONES IMAGENES
    def ejecutar_comprimir_img(self, rutas, calidad):
        if not rutas:
            return {"status": "error", "message": "No hay archivo seleccionado."}
        
        nombre_base, ext = os.path.splitext(rutas[0])
        output_path = f"{nombre_base}_comprimida{ext}"
        return comprimir_imagen(rutas[0], output_path, int(calidad))
    
    def ejecutar_quitar_fondo(self, rutas):
        if not rutas:
            return {"status": "error", "message": "No hay archivo seleccionado."}
        
        nombre_base, _ = os.path.splitext(rutas[0])
        output_path = f"{nombre_base}_sin_fondo.png"
        return quitar_fondo(rutas[0], output_path)
    
    def obtener_imagen_b64(self, ruta):
        if not ruta or not os.path.exists(ruta):
            return ""
        try:
            with open(ruta, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode('utf-8')
                ext = os.path.splitext(ruta)[1].lower().replace('.', '')
                formato = "jpeg" if ext in ["jpg", ""] else ext
                return f"data:image/{formato};base64,{encoded}"
        except Exception:
            return ""

    def ejecutar_recorte(self, rutas, x, y, width, height):
        if not rutas:
            return {"status": "error", "message": "No hay archivo seleccionado."}
        
        nombre_base, ext = os.path.splitext(rutas[0])
        output_path = f"{nombre_base}_recortada{ext}"
        from functions import recortar_interactivo
        return recortar_interactivo(rutas[0], output_path, x, y, width, height)
        
    def ejecutar_marca_agua_texto(self, rutas, texto, color, fuente, posicion):
        if not rutas:
            return {"status": "error", "message": "No hay archivo seleccionado."}
        
        nombre_base, ext = os.path.splitext(rutas[0])
        output_path = f"{nombre_base}_firmada{ext}"
        return agregar_marca_agua_texto(rutas[0], output_path, texto, color, fuente, posicion)

    def ejecutar_marca_agua_imagen(self, rutas, ruta_logo, posicion):
        if not rutas:
            return {"status": "error", "message": "No hay archivo seleccionado."}
        
        nombre_base, ext = os.path.splitext(rutas[0])
        output_path = f"{nombre_base}_con_logo{ext}"
        return agregar_marca_agua_imagen(rutas[0], output_path, ruta_logo, posicion)

api = API()

window = webview.create_window('Herramientas PDF', url='index.html', js_api=api, width=850, height=650)

def on_drag(e):
    pass

def on_drop(e):
    files = e['dataTransfer']['files']
    if len(files) == 0: return
    rutas = [file.get('pywebviewFullPath') for file in files if file.get('pywebviewFullPath')]
    if rutas:
        rutas_json = json.dumps(rutas)
        window.evaluate_js(f"recibirArchivosDePython({rutas_json})")

def bind(window):
    window.dom.document.events.dragenter += DOMEventHandler(on_drag, True, True)
    window.dom.document.events.dragstart += DOMEventHandler(on_drag, True, True)
    window.dom.document.events.dragover += DOMEventHandler(on_drag, True, True, debounce=500)
    window.dom.document.events.drop += DOMEventHandler(on_drop, True, True)

if __name__ == '__main__':
    webview.start(bind, window)