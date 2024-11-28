const eliminaFooter = () => {
    const footer = document.getElementById('footer')
    footer.remove()
}

document.addEventListener('DOMContentLoaded', () => {
    // Eliminamos el footer
    eliminaFooter()
})
