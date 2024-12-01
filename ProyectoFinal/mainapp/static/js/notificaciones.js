document.addEventListener('DOMContentLoaded', function () {   
    const usuario = document.getElementById('data-usuario').getAttribute('data-usuario');
    if (usuario === 'None') {
        return;
    } 

    const notificacionesList = document.getElementById('notificaciones-list');
    const notificacionesCount = document.getElementById('notificaciones-count');

    // Fetch de las notificaciones
    fetch('/notificaciones/')
    .then(response => response.json())
    .then(data => {
        notificacionesList.innerHTML = '';

        if (data.notificaciones && data.notificaciones.length > 0) {
            notificacionesCount.textContent = data.notificaciones.length;

            data.notificaciones.forEach(notificacion => {
                const listItem = document.createElement('li');
                listItem.className = 'dropdown-item unread';

                // Diferenciar el tipo de notificación
                if (notificacion.tipo === 'oferta') {
                    listItem.innerHTML = `
                        <i class="fas fa-tag notificacion-icono"></i>
                        <div class="notificacion-contenido">
                            <div>
                                <strong>${notificacion.emisor} ofreció:</strong> ${notificacion.objeto}
                            </div>
                            <small>${notificacion.comic}</small>
                        </div>
                    `;
                } else if (notificacion.tipo === 'notificacion') {
                    listItem.innerHTML = `
                        <i class="fas fa-bell notificacion-icono"></i>
                        <div class="notificacion-contenido">
                            <div>${notificacion.mensaje}</div>
                            <small>${notificacion.fecha}</small>
                        </div>
                    `;
                }

                // Marcar como vista al hacer clic
                listItem.addEventListener('click', () => {
                    fetch(`/marcar-notificacion-vista/${notificacion.id}/`, { method: 'POST' })
                        .then(() => {
                            listItem.classList.remove('unread');
                            const count = parseInt(notificacionesCount.textContent, 10) - 1;
                            notificacionesCount.textContent = count > 0 ? count : '';
                            if (count === 0) {
                                notificacionesList.innerHTML = '<li class="no-notificaciones">No hay notificaciones</li>';
                            }
                        });
                });

                notificacionesList.appendChild(listItem);
            });
        } else {
            notificacionesList.innerHTML = '<li class="no-notificaciones">No hay notificaciones</li>';
            notificacionesCount.textContent = ''; 
        }
    })
    .catch(error => {
        console.error('Error al obtener notificaciones:', error);
        notificacionesList.innerHTML = '<li class="no-notificaciones">Error al cargar notificaciones</li>';
    });
});
