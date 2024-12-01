// Regresa a la pagina anterior
const backPage = () => {
    // Regresamos a la pagina anterior
    window.history.back();
}

const aceptarOferta = async (idOferta) => {
    let response = null
    try{
        response = await servicioAceptarOferta(idOferta)
        // Si la peticion fu exitosa
        if (response.success){
            actualizaCardOferta(idOferta,'aceptada')
        }
    } catch (error) {
        console.log('Error al intentar aceptar la oferta')
    }
}

const rechazarOferta = async (idOferta) => {
    let response = null
    try{
        response = await servicioRechazarOferta(idOferta)
        // Si la peticion fu exitosa
        if (response.success){
            actualizaCardOferta(idOferta,'rechazada')
        }
    } catch (error) {
        console.log('Error al intentar aceptar la oferta')
    }
}

const servicioAceptarOferta = async (idOferta) => {
    const csrftoken = getCookie('csrftoken')
    const url = `/aceptar_oferta/${idOferta}`
    const response = await fetch(url, {
        method: 'POST',
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

const servicioRechazarOferta = async (idOferta) => {
    const csrftoken = getCookie('csrftoken')
    const url = `/rechazar_oferta/${idOferta}`
    const response = await fetch(url, {
        method: 'POST',
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

const actualizaCardOferta = (idOferta, estatus) => {
    const oferta = document.getElementById(`oferta-${idOferta}`)
    oferta.querySelector('.btn-aceptar').remove()
    oferta.querySelector('.btn-rechazar').remove()
    const p = document.createElement('p')
    const span = document.createElement('span')
    span.classList.add(estatus)
    span.textContent = `Oferta ${estatus}`
    p.appendChild(span)
    oferta.appendChild(p)    
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