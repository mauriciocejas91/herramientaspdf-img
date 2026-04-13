let currentTool = '';
let selectedFiles = []; 
let lastProcessedPath = ''; 
let cropperInstance = null;

function openTool(tool) {
    currentTool = tool;
    selectedFiles = []; 
    lastProcessedPath = '';
    
    document.getElementById('menu-view').classList.remove('active');
    document.getElementById('tool-view').classList.add('active');
    document.getElementById('status').innerText = '';
    document.getElementById('success-actions').style.display = 'none';
    
    const toolTitles = {
        'unir': 'Unir PDFs', 'separar': 'Separar PDF', 'pdf_a_word': 'Convertir PDF a Word',
        'word_a_pdf': 'Convertir Word a PDF', 'comprimir': 'Comprimir PDF', 'pdf_a_img': 'PDF a Imagen',
        'comprimir_img': 'Comprimir Imagen', 'quitar_fondo': 'Quitar Fondo IA',
        'resize_img': 'Redimensionar Imagen', 'crop_img': 'Recortar Imagen interactivo'
    };
    
    const toolButtons = {
        'unir': 'Unir', 'separar': 'Separar', 'pdf_a_word': 'Convertir a Word',
        'word_a_pdf': 'Convertir a PDF', 'comprimir': 'Comprimir', 'pdf_a_img': 'Convertir a Imagen',
        'comprimir_img': 'Comprimir', 'quitar_fondo': 'Eliminar Fondo',
        'resize_img': 'Redimensionar', 'crop_img': 'Aplicar Recorte'
    };

    // Ocultar paneles extra
    if (cropperInstance) {
        cropperInstance.destroy();
        cropperInstance = null;
    }
    document.getElementById('crop-container').style.display = 'none';
    document.getElementById('file-list').style.display = 'flex';

    // Gestionar paneles de opciones
    document.getElementById('options-panel').style.display = 'none';
    document.getElementById('opt-format').style.display = 'none';
    document.getElementById('opt-quality').style.display = 'none';

    if (tool === 'pdf_a_img') {
        document.getElementById('options-panel').style.display = 'flex';
        document.getElementById('opt-format').style.display = 'flex';
    } else if (tool === 'comprimir_img') {
        document.getElementById('options-panel').style.display = 'flex';
        document.getElementById('opt-quality').style.display = 'flex';
    }

    document.getElementById('tool-title').innerText = toolTitles[tool];
    document.getElementById('btn-process').innerText = toolButtons[tool];
    
    renderFileList();
}

function goBack() {
    document.getElementById('tool-view').classList.remove('active');
    document.getElementById('menu-view').classList.add('active');
}

function addFiles() {
    const allowMultiple = currentTool === 'unir'; 
    let fileType = 'pdf';
    
    if (currentTool === 'word_a_pdf') {
        fileType = 'word';
    } else if (currentTool === 'comprimir_img' || currentTool === 'quitar_fondo' || currentTool === 'resize_img' || currentTool === 'crop_img') {
        fileType = 'img';
    }
    
    window.pywebview.api.seleccionar_archivos(allowMultiple, fileType).then(files => {
        if (files && files.length > 0) {
            if (currentTool === 'unir') {
                selectedFiles = selectedFiles.concat(files); 
            } else {
                selectedFiles = files; 
            }
            
            document.getElementById('success-actions').style.display = 'none';
            document.getElementById('status').innerText = '';
            
            // Si la herramienta es recortar, lanzamos la interfaz interactiva
            if (currentTool === 'crop_img') {
                initCropper(selectedFiles[0]);
            } else {
                // Para todas las demás, solo mostramos la lista normal
                renderFileList();
            }
        }
    });
}

function renderFileList() {
    const container = document.getElementById('file-list');
    container.innerHTML = '';
    
    if (selectedFiles.length === 0) {
        container.innerHTML = '<p class="empty-state">No hay archivos seleccionados. Haz clic en "+ Añadir archivos".</p>';
        return;
    }

    selectedFiles.forEach((file, index) => {
        const fileName = file.split('\\').pop().split('/').pop();
        
        const div = document.createElement('div');
        div.className = 'file-item';
        
        div.innerHTML = `
            <span class="file-name">${fileName}</span>
            <div class="item-controls">
                ${currentTool === 'unir' ? `
                    <button class="btn-icon" onclick="moveFile(${index}, -1)" ${index === 0 ? 'disabled' : ''}>↑</button>
                    <button class="btn-icon" onclick="moveFile(${index}, 1)" ${index === selectedFiles.length - 1 ? 'disabled' : ''}>↓</button>
                ` : ''}
                <button class="btn-icon delete" onclick="removeFile(${index})">✕</button>
            </div>
        `;
        container.appendChild(div);
    });
}

function moveFile(index, direction) {
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= selectedFiles.length) return;
    const temp = selectedFiles[index];
    selectedFiles[index] = selectedFiles[newIndex];
    selectedFiles[newIndex] = temp;
    renderFileList();
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    renderFileList();
}

function process() {
    if (selectedFiles.length === 0) return;
    
    const statusDiv = document.getElementById('status');
    statusDiv.innerText = "Procesando, por favor espera...";
    statusDiv.className = '';
    document.getElementById('success-actions').style.display = 'none';

    if (currentTool === 'unir') {
        window.pywebview.api.ejecutar_unir(selectedFiles).then(handleResponse);
    } else if (currentTool === 'separar') {
        window.pywebview.api.ejecutar_separar(selectedFiles).then(handleResponse);
    } else if (currentTool === 'pdf_a_word') {
        window.pywebview.api.ejecutar_pdf_word(selectedFiles).then(handleResponse);
    } else if (currentTool === 'word_a_pdf') {
        window.pywebview.api.ejecutar_word_pdf(selectedFiles).then(handleResponse);
    } else if (currentTool === 'comprimir') {
        window.pywebview.api.ejecutar_comprimir(selectedFiles).then(handleResponse);
    } else if (currentTool === 'pdf_a_img') {
        const formato = document.getElementById('img-format').value;
        window.pywebview.api.ejecutar_pdf_imagen(selectedFiles, formato).then(handleResponse);
    } else if (currentTool === 'comprimir_img') {
        const calidad = document.getElementById('img-quality').value;
        window.pywebview.api.ejecutar_comprimir_img(selectedFiles, calidad).then(handleResponse);
    } else if (currentTool === 'comprimir_img') {
        const calidad = document.getElementById('img-quality').value;
        window.pywebview.api.ejecutar_comprimir_img(selectedFiles, calidad).then(handleResponse);
    } else if (currentTool === 'quitar_fondo') {
        window.pywebview.api.ejecutar_quitar_fondo(selectedFiles).then(handleResponse);
    } else if (currentTool === 'crop_img') {
        if (!cropperInstance) return;
        const cropData = cropperInstance.getData(true); // true devuelve enteros
        window.pywebview.api.ejecutar_recorte(selectedFiles, cropData.x, cropData.y, cropData.width, cropData.height).then(handleResponse);
    }
}

function handleResponse(res) {
    const statusDiv = document.getElementById('status');
    statusDiv.innerText = res.message;
    statusDiv.className = res.status; 
    
    if(res.status === 'success') {
        selectedFiles = []; 
        renderFileList();
        
        lastProcessedPath = res.path;
        document.getElementById('success-actions').style.display = 'flex';
        
        if (currentTool === 'separar' || currentTool === 'pdf_a_img') {
            document.getElementById('btn-view-file').style.display = 'none';
        } else {
            document.getElementById('btn-view-file').style.display = 'block';
        }
    }
}

function abrirArchivo() {
    if (lastProcessedPath) window.pywebview.api.abrir_archivo(lastProcessedPath);
}

function abrirCarpeta() {
    if (lastProcessedPath) window.pywebview.api.abrir_carpeta(lastProcessedPath);
}

// Lógica de Drag & Drop Visual
document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('file-list');
    
    dropZone.addEventListener('click', (e) => {
        if (e.target === dropZone || e.target.classList.contains('empty-state')) {
            addFiles();
        }
    });

    ['dragenter', 'dragover'].forEach(evt => dropZone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    }));

    ['dragleave', 'drop'].forEach(evt => dropZone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    }));
});

function recibirArchivosDePython(rutas) {
    if (!currentTool) return;

    let newPaths = [];
    let extEsperadas = ['.pdf'];
    if (currentTool === 'word_a_pdf') extEsperadas = ['.docx'];
    if (currentTool === 'comprimir_img' || currentTool === 'quitar_fondo') extEsperadas = ['.jpg', '.jpeg', '.png', '.webp', '.avif'];

    for (let i = 0; i < rutas.length; i++) {
        const filePath = rutas[i].toLowerCase();
        if (extEsperadas.some(ext => filePath.endsWith(ext))) {
            newPaths.push(rutas[i]);
        }
    }

    if (newPaths.length > 0) {
        if (currentTool === 'unir') {
            selectedFiles = selectedFiles.concat(newPaths);
        } else {
            selectedFiles = [newPaths[0]];
        }
        
        document.getElementById('success-actions').style.display = 'none';
        document.getElementById('status').innerText = '';
        document.getElementById('file-list').classList.remove('dragover');
        renderFileList();
    }
}

function initCropper(filePath) {
    document.getElementById('file-list').style.display = 'none';
    document.getElementById('crop-container').style.display = 'block';
    
    window.pywebview.api.obtener_imagen_b64(filePath).then(b64 => {
        const imageElement = document.getElementById('crop-image');
        imageElement.src = b64;
        
        if (cropperInstance) {
            cropperInstance.destroy();
        }
        
        cropperInstance = new Cropper(imageElement, {
            viewMode: 1,
            dragMode: 'crop',
            autoCropArea: 0.8,
            restore: false,
            guides: true,
            center: true,
            highlight: false,
            cropBoxMovable: true,
            cropBoxResizable: true,
            toggleDragModeOnDblclick: false,
        });
    });
}