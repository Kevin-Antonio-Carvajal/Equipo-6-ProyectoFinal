document.addEventListener('DOMContentLoaded', function () {
    const notificacionesList = document.getElementById('notificaciones-list');
    const notificacionesCount = document.getElementById('notificaciones-count');

    // Fetch de las notificaciones no vistas
    fetch('/notificaciones/')
    .then(response => response.json())
    .then(data => {
        const notificacionesList = document.getElementById('notificaciones-list');
        const notificacionesCount = document.getElementById('notificaciones-count');
        notificacionesList.innerHTML = '';

        if (data.ofertas && data.ofertas.length > 0) {
            notificacionesCount.textContent = data.ofertas.length;

            data.ofertas.forEach(oferta => {
                const listItem = document.createElement('li');
                listItem.className = 'dropdown-item unread'; 

                listItem.innerHTML = `
                    <i class="fas fa-tag notificacion-icono"></i>
                    <div class="notificacion-contenido">
                        <div>
                            <strong>${oferta.emisor} ofreció:</strong> ${oferta.objeto}
                        </div>
                        <small>${oferta.comic}</small>
                    </div>
                `;
            
            
                // Marcar como vista al hacer clic
                listItem.addEventListener('click', () => {
                    fetch(`/marcar-notificacion-vista/${oferta.id}/`, { method: 'POST' })
                        .then(() => {
                            listItem.classList.remove('unread');
                            const count = parseInt(notificacionesCount.textContent, 10) - 1;
                            notificacionesCount.textContent = count > 0 ? count : '';
                            if (count === 0) {
                                notificacionesList.innerHTML = '<li class="no-notificaciones">No hay ofertas</li>';
                            }
                        });
                });

                notificacionesList.appendChild(listItem);
            });
        } else {
            notificacionesList.innerHTML = '<li class="no-notificaciones">No hay ofertas</li>';
            notificacionesCount.textContent = ''; 
        }
    })
    .catch(error => {
        console.error('Error al obtener notificaciones:', error);
        document.getElementById('notificaciones-list').innerHTML = '<li class="no-notificaciones">Error al cargar ofertas</li>';
    });
});
