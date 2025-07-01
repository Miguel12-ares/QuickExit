/* Este archivo JavaScript ha sido movido a la carpeta 'usuarios' para centralizar la lógica de búsqueda y gestión de usuarios. */
document.addEventListener('DOMContentLoaded', function() {
    const buscadorForm = document.getElementById('buscador-usuarios');
    const tablaBody = document.querySelector('.admin-table tbody');
    const btnBuscar = document.getElementById('btn-buscar-usr');
    const btnLimpiar = document.getElementById('btn-limpiar-usr');

    // Debounce para evitar demasiadas peticiones
    let debounceTimeout = null;
    function debounceCargarUsuarios() {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(cargarUsuarios, 250);
    }

    function cargarUsuarios() {
        const formData = new FormData(buscadorForm);
        const queryParams = new URLSearchParams();
        for (const [key, value] of formData.entries()) {
            if (value) {
                queryParams.append(key, value);
            }
        }

        fetch(`/admin/api/buscar_usuarios?${queryParams.toString()}`)
            .then(response => response.json())
            .then(data => {
                tablaBody.innerHTML = ''; // Limpiar la tabla
                if (data.usuarios && data.usuarios.length > 0) {
                    data.usuarios.forEach(usuario => {
                        const row = tablaBody.insertRow();
                        row.insertCell().textContent = usuario.documento;
                        row.insertCell().textContent = usuario.nombre;
                        row.insertCell().textContent = usuario.email;
                        row.insertCell().textContent = usuario.rol;
                        row.insertCell().textContent = usuario.ficha ? `${usuario.ficha.nombre} (${usuario.ficha.id_ficha})` : 'N/A';
                        // Selector para cambiar el estado de validación del usuario
                        const validadoCell = row.insertCell();
                        validadoCell.innerHTML = `
                            <select name="validado" class="estado-select${!usuario.validado ? ' desactivado' : ''}" data-user-id="${usuario.id_usuario}">
                                <option value="true" ${usuario.validado ? 'selected' : ''}>Activo</option>
                                <option value="false" ${!usuario.validado ? 'selected' : ''}>Inactivo</option>
                            </select>
                        `;
                        // Añadir event listener al select después de que se ha añadido al DOM
                        const estadoSelect = validadoCell.querySelector('.estado-select');
                        estadoSelect.addEventListener('change', function() {
                            const userId = this.dataset.userId;
                            const newStatus = this.value;
                            actualizarEstadoUsuario(userId, newStatus);
                        });

                        const accionesCell = row.insertCell();
                        // Botón de eliminar
                        const deleteButton = document.createElement('button');
                        deleteButton.innerHTML = '<i class="fas fa-trash"></i> Eliminar';
                        deleteButton.classList.add('btn', 'btn-delete');
                        deleteButton.dataset.id = usuario.id_usuario;
                        deleteButton.addEventListener('click', function() {
                            eliminarUsuario(usuario.id_usuario, usuario.nombre);
                        });
                        accionesCell.appendChild(deleteButton);
                    });
                } else {
                    const row = tablaBody.insertRow();
                    const cell = row.insertCell();
                    cell.colSpan = 7; // Ajustar al número de columnas
                    cell.textContent = 'No se encontraron usuarios.';
                    cell.style.textAlign = 'center';
                    cell.style.color = '#888';
                    cell.style.fontStyle = 'italic';
                    cell.style.padding = '2rem';
                }
            })
            .catch(error => {
                console.error('Error al cargar usuarios:', error);
                showError('Error al cargar usuarios. Revisa la consola para más detalles.');
            });
    }

    function eliminarUsuario(id_usuario, nombre_usuario) {
        // Primera validación
        QuickExitNotifications.show({
            type: 'warning',
            title: 'Primera Confirmación',
            message: `¿Estás seguro de que quieres eliminar a ${nombre_usuario}? Esta acción es irreversible.`,
            duration: 0,
            dismissible: true,
            actions: [
                {
                    text: 'Cancelar',
                    type: 'secondary',
                    icon: 'fas fa-times',
                    callback: () => {}
                },
                {
                    text: 'Continuar',
                    type: 'primary',
                    icon: 'fas fa-arrow-right',
                    callback: () => {
                        // Segunda validación
                        QuickExitNotifications.show({
                            type: 'danger',
                            title: 'Confirmación Final',
                            message: `Esta es la última confirmación. ¿Realmente deseas eliminar a ${nombre_usuario}?`,
                            duration: 0,
                            dismissible: true,
                            actions: [
                                {
                                    text: 'Cancelar',
                                    type: 'secondary',
                                    icon: 'fas fa-times',
                                    callback: () => {}
                                },
                                {
                                    text: 'Eliminar',
                                    type: 'primary',
                                    icon: 'fas fa-trash',
                                    callback: () => {
                                        fetch(`/admin/api/eliminar_usuario/${id_usuario}`, {
                                            method: 'POST',
                                            headers: {
                                                'X-Requested-With': 'XMLHttpRequest',
                                            },
                                        })
                                        .then(response => response.json())
                                        .then(data => {
                                            if (data.success) {
                                                showSuccess(data.message);
                                                cargarUsuarios();
                                            } else {
                                                showError(data.message || 'No se pudo eliminar el usuario.');
                                            }
                                        })
                                        .catch(error => {
                                            console.error('Error al eliminar usuario:', error);
                                            showError('Ocurrió un error al eliminar el usuario.');
                                        });
                                    }
                                }
                            ]
                        });
                    }
                }
            ]
        });
    }

    function actualizarEstadoUsuario(id_usuario, nuevo_estado) {
        fetch(`/admin/api/actualizar_estado_usuario/${id_usuario}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded', // Para enviar como form data
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: `validado=${nuevo_estado}`,
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showSuccess(data.message);
                cargarUsuarios(); // Recargar la tabla para reflejar los cambios
            } else if (data.error) {
                showError(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error al actualizar estado:', error);
            showError('Ocurrió un error al actualizar el estado del usuario.');
        });
    }

    // Event Listeners
    buscadorForm.querySelectorAll('input[type="text"], input[type="email"], input[type="number"]').forEach(input => {
        input.addEventListener('input', debounceCargarUsuarios);
    });
    
    buscadorForm.querySelector('select[name="buscar_rol"]').addEventListener('change', debounceCargarUsuarios);

    btnBuscar.addEventListener('click', cargarUsuarios);
    btnLimpiar.addEventListener('click', function() {
        buscadorForm.reset();
        cargarUsuarios(); // Cargar todos los usuarios después de limpiar
    });

    // Cargar usuarios al cargar la página inicialmente
    cargarUsuarios();
}); 