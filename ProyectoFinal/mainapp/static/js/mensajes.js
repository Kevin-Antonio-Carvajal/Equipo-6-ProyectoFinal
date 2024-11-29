const eliminaFooter = () => {
    const footer = document.getElementById('footer')
    footer.remove()
}

const abrirChat = async (id_usuario) => {
    // Verificamos que el chat no haya sido abierto antes
    const contenedorChatAbierto = document.getElementById('chat-abierto-contenedor')
    const chatAbiertoId = contenedorChatAbierto.getAttribute('data-chat-abierto-id')
    if (String(id_usuario) === chatAbiertoId){
        console.log('El chat ya está abierto')
        return
    }
    try{
        const csrftoken = getCookie('csrftoken')
        const url = `/get_mensajes/${id_usuario}/`
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
                'accept': 'application/json'
            },
            credentials: 'same-origin'
        })
        if (response.ok){
            const data = await response.json()
            const mensajes = data.mensajes
            // Montamos los componentes del chat abierto
            montarChatAbierto(data)
        } else {
            console.log(`Error en la peticion ${response.status}`)
            return
        }
    } catch(error) {
        console.log(`Error al intentar recuperar los mensajes: ${error}`)
    }
}
/**
 * Monta los componentes necesarios para mostrar los mensajes de una forma bonita
 * @param {*} nombre nombre de la persona con la que se está chateando
 * @param {*} mensajes mensajes del chat
 */
const montarChatAbierto = (data) => {    
    // Informacion del usuario del chat
    const usuarioChat = data['usuario_chat']
    const nombreUsuarioChat = usuarioChat['username']
    const idUsuarioChat = usuarioChat['id']
    // Informacion del usuario que inicio sesion
    const usuarioActual = data['usuario_actual']
    const nombreUsuarioActual = usuarioActual['username']
    const idUsuarioActual = usuarioActual['id']
    // Mensajes
    const mensajes = data['mensajes']
    // Contenedor
    const contenedorChatAbierto = document.getElementById('chat-abierto-contenedor')
    // Agregamos el id del chat abierto
    contenedorChatAbierto.setAttribute('data-chat-abierto-id', idUsuarioChat)
    // Encabezado
    const encabezadoChatAbierto = crearEncabezadoChatAbierto(nombreUsuarioChat)
    // Mensajes
    const mensajesChatAbierto = crearMensajesChatAbierto(idUsuarioActual, idUsuarioChat, mensajes)
    // Barra mensajear
    const barraMensajear = crearBarraMensajearChatAbierto(idUsuarioActual, idUsuarioChat)
    // Remplazamos el contenido del contenedor por los elementos
    contenedorChatAbierto.replaceChildren(
        encabezadoChatAbierto,
        mensajesChatAbierto,
        barraMensajear
    )    
}

const crearEncabezadoChatAbierto = (nombre) => {
    // Crear el contenedor principal
    const encabezado = document.createElement('div');
    encabezado.id = 'encabezado';
    // Crear el contenedor de la imagen
    const imagenContenedor = document.createElement('div');
    imagenContenedor.classList.add('imagen-contenedor');
    // Crear el elemento de la imagen
    const imagen = document.createElement('img');
    imagen.src = '/static/images/default_user.png'; // Ruta de la imagen predeterminada
    imagen.alt = 'Imagen del usuario';
    // Agregar la imagen al contenedor de la imagen
    imagenContenedor.appendChild(imagen);
    // Crear el párrafo con el nombre del comprador
    const nombreComprador = document.createElement('p');
    nombreComprador.classList.add('nombre-comprador');
    // Crear el span con el nombre en negritas
    const boldNombre = document.createElement('span');
    boldNombre.classList.add('bold');
    boldNombre.textContent = nombre; // Asignar el nombre pasado como parámetro
    // Agregar el span al párrafo
    nombreComprador.appendChild(boldNombre);
    // Agregar el contenedor de la imagen y el párrafo al encabezado
    encabezado.appendChild(imagenContenedor);
    encabezado.appendChild(nombreComprador);
    return encabezado; // Retorna el elemento creado
}

const crearMensajesChatAbierto = (idUsuarioActual, idUsuarioChat, mensajes) => {
    // Contenedor de los mensajes
    const contenedorMensajes = document.createElement('div')    
    contenedorMensajes.id = 'mensajes-contenedor'
    // Creamos el componente para cada mensaje
    for (let i = 0 ; i < mensajes.length ; i++){
        const mensaje = mensajes[i]
        const esUltimo = i === mensajes.length - 1; // Verificar si es el último mensaje
        // Si el mensaje lo envió el usuario actual:
        let mensajeChatAbierto = null
        if (mensaje['emisor_id']==idUsuarioActual){
            mensajeChatAbierto = crearMensajeUsuarioActual(mensaje['contenido'], esUltimo && mensaje['emisor_id'] === idUsuarioActual);
        } else {
            mensajeChatAbierto = crearMensajeUsuarioChat(mensaje['contenido'], esUltimo && mensaje['emisor_id'] === idUsuarioChat);
        }
        contenedorMensajes.appendChild(mensajeChatAbierto)
    }
    return contenedorMensajes
}

const crearMensajeUsuarioActual = (mensaje, esUltimo) => {
    // Crear el contenedor principal
    const contenedor = document.createElement('div');
    contenedor.classList.add('mensaje', 'usuario-actual');
    if (esUltimo) {
        contenedor.classList.add('ultimo-mensaje');
    }

    // Crear el párrafo para el contenido
    const contenido = document.createElement('p');
    contenido.classList.add('contenido');
    contenido.textContent = mensaje;

    // Crear el contenedor de la imagen
    const imagenContenedor = document.createElement('div');
    imagenContenedor.classList.add('imagen-contenedor');

    // Crear el elemento de la imagen
    const imagen = document.createElement('img');
    imagen.src = '/static/images/default_user.png';
    imagen.alt = 'Imagen del usuario';

    // Añadir la imagen al contenedor de la imagen
    imagenContenedor.appendChild(imagen);

    // Ordenar los elementos: contenido seguido de imagen
    contenedor.appendChild(contenido);
    contenedor.appendChild(imagenContenedor);

    return contenedor;
};

const crearMensajeUsuarioChat = (mensaje, esUltimo) => {
    // Crear el contenedor principal
    const contenedor = document.createElement('div');
    contenedor.classList.add('mensaje', 'usuario-chat');
    if (esUltimo) {
        contenedor.classList.add('ultimo-mensaje');
    }

    // Crear el párrafo para el contenido
    const contenido = document.createElement('p');
    contenido.classList.add('contenido');
    contenido.textContent = mensaje;

    // Crear el contenedor de la imagen
    const imagenContenedor = document.createElement('div');
    imagenContenedor.classList.add('imagen-contenedor');

    // Crear el elemento de la imagen
    const imagen = document.createElement('img');
    imagen.src = '/static/images/default_user.png';
    imagen.alt = 'Imagen del usuario';

    // Añadir la imagen al contenedor de la imagen
    imagenContenedor.appendChild(imagen);

    // Ordenar los elementos: imagen seguida de contenido
    contenedor.appendChild(imagenContenedor);
    contenedor.appendChild(contenido);

    return contenedor;
};

const crearBarraMensajearChatAbierto = (idUsuarioActual, idUsuarioChat) => {
    // Crear el contenedor principal
    const barraMensajear = document.createElement('div');
    barraMensajear.id = 'barra-mensajear';
    // Crear el ícono de hacer oferta
    const iconoOferta = document.createElement('i');
    iconoOferta.classList.add('fa-solid', 'fa-arrow-right-arrow-left');
    iconoOferta.setAttribute('data-bs-toggle', 'tooltip');
    iconoOferta.setAttribute('title', 'Hacer oferta');
    iconoOferta.setAttribute('data-id-usuario-actual', idUsuarioActual);
    iconoOferta.setAttribute('data-id-usuario-chat', idUsuarioChat);
    iconoOferta.setAttribute('onclick', 'mandarOferta(event)');
    // Crear el formulario
    const formulario = document.createElement('form');
    formulario.id = 'formulario-mandar-mensaje';
    formulario.setAttribute('data-id-usuario-actual', idUsuarioActual);
    formulario.setAttribute('data-id-usuario-chat', idUsuarioChat);
    formulario.setAttribute('onsubmit', 'mandarMensaje(event)');
    // Crear el campo de entrada
    const inputMensaje = document.createElement('input');
    inputMensaje.setAttribute('name', 'mensaje');
    inputMensaje.setAttribute('type', 'text');
    inputMensaje.setAttribute('placeholder', 'Aa');
    inputMensaje.setAttribute('oninput', 'verificarContenido(event)');
    // Crear el botón de enviar mensaje
    const botonEnviar = document.createElement('button');
    botonEnviar.id = 'boton-enviar-mensaje';
    botonEnviar.setAttribute('type', 'submit');
    // Crear el ícono dentro del botón
    const iconoEnviar = document.createElement('i');
    iconoEnviar.classList.add('fa-solid', 'fa-paper-plane');
    // Agregar el ícono al botón
    botonEnviar.appendChild(iconoEnviar);
    // Agregar el campo de entrada y el botón al formulario
    formulario.appendChild(inputMensaje);
    formulario.appendChild(botonEnviar);
    // Agregar el ícono de oferta y el formulario al contenedor principal
    barraMensajear.appendChild(iconoOferta);
    barraMensajear.appendChild(formulario);
    return barraMensajear;
};

const mandarOferta = async (event) => {
    // Id del usuario actual
    const idUsuarioActual = event.target.getAttribute('data-id-usuario-actual')
    // Id del usuario del chat
    const idUsuarioChat = event.target.getAttribute('data-id-usuario-chat')
}

const mandarMensaje = async (event) => {
    event.preventDefault()    
    const formulario = event.target
    const formData = new FormData(formulario)
    const mensaje = formData.get('mensaje')
    // Input para escribir el mensaje
    const input = formulario.querySelector("input[type='text']")    
    // Verificamos que el contenido del mensaje no esté vacio
    if (mensaje.trim() === ''){
        // No enviamos el mensaje
        console.log('no enviamos el mensaje')
        return
    }
    // Boton para enviar mensaje    
    const botonEnviarMensaje = document.getElementById('boton-enviar-mensaje')
    // Verificar si el botón está deshabilitado
    if (botonEnviarMensaje.disabled) {
        console.log('El botón está deshabilitado. No se puede enviar el mensaje.');
        return;
    }
    // Id del usuario actual
    const idUsuarioActual = event.target.getAttribute('data-id-usuario-actual')
    // Id del usuario del chat
    const idUsuarioChat = event.target.getAttribute('data-id-usuario-chat')
    // Agregamos la informacion necesaria
    formData.append('idUsuarioEmisor', idUsuarioActual)
    formData.append('idUsuarioReceptor', idUsuarioChat)        
    try {
        // Deshabilitamos el boton de enviar mensaje
        botonEnviarMensaje.disabled = true
        botonEnviarMensaje.classList.add('disabled')
        // Eliminamos el contenido del input
        input.value = ''
        // Mandamos el mensaje
        const response = await servicioMandarMensaje(formData)
        // Si la peticion fue exitosa
        if (response.success) {
            console.log(`Respuesta exito: ${response.message}`)
            // Agregamos el mensaje
            agregarMensaje(formData)
        } else {
            console.log(`Respuesta error: ${response.error}`)
        }
    } catch (error) {
        console.log(`Hubo un error al mandar el mensaje ${error}`)
    } finally {
        // Habilitamos el boton de enviar mensaje
        botonEnviarMensaje.disabled = false
        botonEnviarMensaje.classList.remove('disabled')
    }
}

const agregarMensaje = (formData) => {
    // Obtenemos el último mensaje del contenedor
    const ultimoMensaje = getUltimoMensaje()
    // Verificamos si el ultimo mensaje es de nosotros
    if (ultimoMensaje.classList.contains('usuario-actual')){
        // Le eliminamos la clase de ultimo mensaje
        ultimoMensaje.classList.remove('ultimo-mensaje')
    }
    // Obtenemos el contenido del mensaje
    const mensaje = formData.get('mensaje')
    // Creamos el elemento para agregar al contenedor de mensajes
    const mensajeChatAbierto = crearMensajeUsuarioActual(mensaje, true)
    // Lo agregamos la contenedor
    const contenedorMensajes = document.getElementById('mensajes-contenedor')
    contenedorMensajes.append(mensajeChatAbierto)
    // Actualizamos el panel de chats
    const idChat = formData.get('idUsuarioReceptor')    
    // Obtenemos el chat correspondiente al usuario
    const chatAbierto = getChatAbierto(idChat)
    // Contenedor de chats
    const contenedorChats = document.getElementById('chats-contenedor')
    // Lo ponemos al inicio del contenedor de chats
    contenedorChats.prepend(chatAbierto)
    // Actualizamos la hora y el ultimo mensaje del chat
    const hora = fechaActual = formatoFecha(new Date());
    chatAbierto.querySelector('.ultimo-mensaje').textContent = truncarCadena(mensaje)
    chatAbierto.querySelector('.hora-ultimo-mensaje').textContent = hora
}

const truncarCadena = (cadena) => {
    const limite = 23; // Máximo de caracteres permitidos
    if (cadena.length > limite) {
        return cadena.slice(0, limite) + '...';
    }
    return cadena; // Si no supera el límite, se devuelve la cadena original
}

const formatoFecha = (fecha) => {
    // Convertimos la fecha a un objeto Date
    const fechaMensaje = new Date(fecha);
    const fechaActual = new Date();

    // Calcular la diferencia en días
    const diferenciaTiempo = fechaActual - fechaMensaje; // Diferencia en milisegundos
    const diferenciaDias = Math.floor(diferenciaTiempo / (1000 * 60 * 60 * 24)); // Convertir a días

    if (diferenciaDias === 0) {
        // Si es el mismo día, mostrar la hora (HH:MM)
        const horas = String(fechaMensaje.getHours()).padStart(2, '0');
        const minutos = String(fechaMensaje.getMinutes()).padStart(2, '0');
        return `${horas}:${minutos}`;
    }

    // Si no es el mismo día, mostrar "X d"
    return `${diferenciaDias} d`;
}

const getChatAbierto = (idChat) => {
    // Contenedor de chats
    const contenedorChats = document.getElementById('chats-contenedor')
    const chatAbierto = contenedorChats.querySelector(`#chat-${idChat}`)
    return chatAbierto
}

const getUltimoMensaje = () => {
    // Contenedor de mensajes
    const contenedorMensajes = document.getElementById('mensajes-contenedor')
    return contenedorMensajes.lastElementChild
}

const servicioMandarMensaje = async (formData) => {    
    const csrftoken = getCookie('csrftoken')
    const url = `/mandar_mensaje/`
    const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrftoken,
            'accept': 'application/json'
        },
        credentials: 'same-origin'
    })
    if (!response.ok) {
        throw new Error(`Error en la peticion: ${response.status}`)
    }
    const data = await response.json()
    return data
}

const verificarContenido = (event) => {
    const input = event.target
    const botonEnviarMensaje = document.getElementById('boton-enviar-mensaje')
    if (input.value.trim() !== '') {
        // Aparecemos el boton de enviar        
        botonEnviarMensaje.style.display = 'block'
    } else {
        // Desaparecemos el boton de enviar        
        botonEnviarMensaje.style.display = 'none'
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

document.addEventListener('DOMContentLoaded', () => {
    // Eliminamos el footer
    eliminaFooter()
})
