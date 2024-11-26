// Regresa a la pagina anterior
const backPage = () => {
    // Regresamos a la pagina anterior
    window.history.back();
}

const eliminarComic = async (id_comic) => {
    try{
        const csrftoken = getCookie('csrftoken')
        const url = `/lista_deseos/eliminar/${id_comic}/`
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin'
        })
        if (!response.ok){
            console.log(`Error en la peticion: ${response.status}`)
            return
        }else{
            const data = await response.json()
            // Eliminamos el comic 
            const comic = document.getElementById(`comic-${id_comic}`)
            comic.remove()
            // Verificamos si ya no hay comics en la lista de deseos
            const listaDeseos = document.getElementById('lista-deseos')
            if (listaDeseos.children.length === 0) {
                const notFound = document.getElementById('not-found')
                notFound.classList.remove('hidden')
            }
        }
        
    } catch(error) {
        console.log(`Error al intentar eliminar el comic: ${error}`)
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