/* Este archivo JavaScript ha sido movido a la carpeta 'usuarios' para centralizar la lógica de búsqueda y gestión de usuarios. */
document.addEventListener('DOMContentLoaded', function() {
    const buscadorForm = document.getElementById('buscador-usuarios');
    const tablaBody = document.querySelector('.admin-table tbody');
    const btnBuscar = document.getElementById('btn-buscar-usr');
    const btnLimpiar = document.getElementById('btn-limpiar-usr');

    function cargarUsuarios() {
        const formData = new FormData(buscadorForm);
        const queryParams = new URLSearchParams();
        for (const [key, value] of formData.entries()) {
            if (value) {
                queryParams.append(key, value);
            }
        }

        fetch(`/api/buscar_usuarios?${queryParams.toString()}`)
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
                            if (confirm(`¿Estás seguro de que quieres eliminar a ${usuario.nombre}?`)) {
                                eliminarUsuario(usuario.id_usuario);
                            }
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
                alert('Error al cargar usuarios. Revisa la consola para más detalles.');
            });
    }

    function eliminarUsuario(id_usuario) {
        fetch(`/admin/eliminar_usuario/${id_usuario}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => {
            // Intentar obtener el JSON incluso si hay error
            return response.json().then(data => {
                return { status: response.status, ok: response.ok, data: data };
            });
        })
        .then(result => {
            if (result.ok) {
                alert(result.data.message);
                cargarUsuarios(); // Recargar la tabla después de eliminar
            } else {
                // Mostrar el mensaje específico del servidor
                console.error(`Error ${result.status}:`, result.data);
                alert(result.data.message || `Error ${result.status}: ${result.data.error || 'Error desconocido'}`);
            }
        })
        .catch(error => {
            console.error('Error al eliminar usuario:', error);
            alert(`Ocurrió un error al intentar eliminar el usuario: ${error.message}`);
        });
    }

    function actualizarEstadoUsuario(id_usuario, nuevo_estado) {
        fetch(`/admin/actualizar_estado_usuario/${id_usuario}`, {
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
                alert(data.message);
                cargarUsuarios(); // Recargar la tabla para reflejar los cambios
            } else if (data.error) {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error al actualizar estado:', error);
            alert('Ocurrió un error al actualizar el estado del usuario.');
        });
    }

    // Event Listeners
    btnBuscar.addEventListener('click', cargarUsuarios);
    btnLimpiar.addEventListener('click', function() {
        buscadorForm.reset();
        cargarUsuarios(); // Cargar todos los usuarios después de limpiar
    });

    // Cargar usuarios al cargar la página inicialmente
    cargarUsuarios();
}); 