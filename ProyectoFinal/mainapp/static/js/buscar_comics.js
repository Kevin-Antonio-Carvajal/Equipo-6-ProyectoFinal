// Evento que se dispara al cargar la pagina
document.addEventListener('DOMContentLoaded', () => {
    // Obtenemos la barra de busqueda
    const barraBusqueda = document.getElementById('barra-busqueda')
    const input = barraBusqueda.querySelector("input[type='search']")
    // Obtenemos lo que el usuario busco
    const dataBusqueda = document.getElementById('data-busqueda').getAttribute('data-busqueda')
    // Le ponermos lo que busco el usuario
    input.value = dataBusqueda
})