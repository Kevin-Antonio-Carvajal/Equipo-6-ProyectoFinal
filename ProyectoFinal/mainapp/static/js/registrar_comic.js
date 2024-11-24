// Regresa a la pagina anterior
const backPage = () => {
    // Regresamos a la pagina anterior
    window.history.back();
}

// Verifica el tipo de archivo
const validarArchivoImagen = (file) => {
    return file && (file.type === 'image/jpeg' || file.type === 'image/png');
};

// Agrega los eventos al label de la imagen
const cargaEventosLabelImagen = () => {
    const dropzone = document.getElementById('dropzone-image');
    const inputImagen = document.getElementById('input-imagen');

    // Prevenir el comportamiento predeterminado de arrastrar y soltar
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, e => e.preventDefault());
        dropzone.addEventListener(eventName, e => e.stopPropagation());
    });

    // Cambiar estilos al arrastrar la imagen
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'));
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'));
    });

    // Manejar el evento de "drop"
    dropzone.addEventListener('drop', e => {
        const files = e.dataTransfer.files;

        // Verificar que se haya soltado un archivo y que sea una imagen
        if (files.length && validarArchivoImagen(files[0])) {
            // Asignar el archivo al input
            inputImagen.files = files;
            console.log(`Archivo cargado: ${files[0].name}`);
            mostrarVistaPrevia(files[0]); // Mostrar vista previa
        } else {
            alert('Por favor, sube un archivo PNG o JPG.');
        }
    });
};

// Agrega los eventos al input de la imagen
const cargaEventosInputImagen = () => {
    const inputImagen = document.getElementById('input-imagen');

    inputImagen.addEventListener('change', (event) => {
        const file = event.target.files[0];

        // Validar que se haya seleccionado un archivo y sea una imagen
        if (validarArchivoImagen(file)) {
            mostrarVistaPrevia(file);
        } else {
            alert('Por favor, selecciona un archivo PNG o JPG válido.');
        }
    });
};

// Muestra la imagen
const mostrarVistaPrevia = (file) => {
    const imagenContainer = document.getElementById('imagen-container');
    const reader = new FileReader();

    // Leer el archivo como URL de datos
    reader.onload = (e) => {
        // Crear un nuevo elemento <img>
        const img = document.createElement('img');
        img.src = e.target.result; // Asignar la imagen cargada como fuente
        img.alt = 'Vista previa de la imagen';
        // Reemplazar todos los hijos del contenedor con la nueva imagen
        imagenContainer.replaceChildren(img, crearTache());
    };

    reader.readAsDataURL(file); // Leer el archivo seleccionado
};

// Funcion que crea un elemento para eliminar una imagen y lo regresa
const crearTache = () => {
    const tache = document.createElement('i')
    tache.className = 'fa-solid fa-x tache'
    tache.setAttribute('data-bs-toggle', 'tooltip')
    tache.setAttribute('title', 'Eliminar imagen')
    tache.addEventListener('click', () => {
        limpiarInputImagen();
        const imagenContainer = document.getElementById('imagen-container')
        // Eliminamos los hijos del contenedor y agregamos el label otra vez
        imagenContainer.replaceChildren(crearLabelCargarImagen())
        // Volvemos a cargar los eventos para el label
        cargaEventosLabelImagen();
    })
    return tache
}

// Funcion que crea un elemento para cargar una iamgen y lo regresa
const crearLabelCargarImagen = () => {
    const label = document.createElement('label')
    label.id = 'dropzone-image'
    label.htmlFor = 'input-imagen'
    const div = document.createElement('div')
    div.className = 'imagen-info'
    const i = document.createElement('i')
    i.className = 'fa-solid fa-arrow-up-from-bracket'
    const p1 = document.createElement('p')
    const span = document.createElement('span')
    span.className = 'bold'
    span.textContent = 'Haz click para subir'
    const texto = document.createTextNode(' o arrastra y suelta')
    p1.appendChild(span)
    p1.appendChild(texto)
    const p2 = document.createElement('p')
    p2.textContent = 'un archivo PNG o JPG'
    div.appendChild(i)
    div.appendChild(p1)
    div.appendChild(p2)
    label.appendChild(div)
    return label
}

// Elimina la imagen cargada en el input
const limpiarInputImagen = () => {
    const inputImagen = document.getElementById('input-imagen');
    inputImagen.value = ''; // Limpia el archivo cargado sin eliminar el input
};

const cargaEventosFormularioComic = () => {
    const formularioComic = document.getElementById('formulario-comic')
    formularioComic.addEventListener('submit', async (event) => {
        event.preventDefault()
        // Deshabilitamos el boton de registrar comic
        const botonEnviar = formularioComic.querySelector('input[type="submit"]')
        botonEnviar.disabled = true
        botonEnviar.classList.add('disabled')
        // FormData
        const formData = new FormData(formularioComic)
        // Accedemos a los valores del formulario
        const titulo = formData.get('nombre')
        const descripcion = formData.get('descripcion')
        const imagen = formData.get('imagen')
        // Verificamos que se haya cargado una imagen
        if (!imagen.size){
            // Agregamos mensaje de error
            const mensajesImagenContainer = document.getElementById('mensajes-imagen')
            const mensajeError = crearMensajeError('Debes agregar una imagen del cómic')
            mensajesImagenContainer.replaceChildren(mensajeError)
            return
        }
        // Enviamos los datos al backend para crear el nuevo comic
        try{
            // Esperamos la resolucion            
            const response = await servicioCrearNuevoComic(formData)
            // Si la peticion fue exitosa
            if (response.success) {
                console.log(`Respuesta: ${response.message}`)
            } else {
                console.log(`Respuesta: ${response.error}`)
            }
        } catch(error) {
            console.log(`Hubo un error mientras se esperaba la creacion del nuevo comic ${error}`)
        } finally{
            // Habilitamos el boton nuevamente
            botonEnviar.disabled = false
            botonEnviar.classList.remove('disabled')
            // Redirigimos a la pagina principal
            window.location.href = '/inicio'
        }
    })
}

const servicioCrearNuevoComic = async (formData) => {    
    try{
        const csrftoken = getCookie('csrftoken')
        const url = `/crear_comic/`
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken
            },
            credentials: 'same-origin'
        })
        const data = await response.json()
        return data
    } catch (error) {
        console.log('Hubo un error al intentar mandar la informacion')
        throw error
    }
}

/**
 * Funcion que regresa una Cookie
 * @param {*} name nombre de la cookie
 * @returns 
 */
const getCookie = (name) => {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const crearMensajeError = (mensaje) => {
    const p = document.createElement('p')
    p.className = 'mensaje-error'
    p.textContent = mensaje
    return p
}

// Evento que se dispara al cargarse el contenido
document.addEventListener('DOMContentLoaded', () => {
    cargaEventosLabelImagen();
    cargaEventosInputImagen();
    cargaEventosFormularioComic();
});