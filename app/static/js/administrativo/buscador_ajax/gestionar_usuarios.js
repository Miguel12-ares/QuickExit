document.addEventListener('DOMContentLoaded', function() {
    const buscadorForm = document.getElementById('buscador-usuarios');
    const tablaBody = document.querySelector('.usuarios-table tbody');
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
                        row.insertCell().innerHTML = `
                            <span class="badge ${usuario.validado ? 'badge-activo' : 'badge-inactivo'}">
                                ${usuario.validado ? 'Activo' : 'Inactivo'}
                            </span>
                        `;
                        const accionesCell = row.insertCell();
                        // Botón de eliminar
                        const deleteButton = document.createElement('button');
                        deleteButton.textContent = 'Eliminar';
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
                }
            })
            .catch(error => console.error('Error al cargar usuarios:', error));
    }

    function eliminarUsuario(id_usuario) {
        fetch(`/admin/eliminar_usuario/${id_usuario}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            // Si necesitas enviar datos en el cuerpo, hazlo aquí
            // body: JSON.stringify({ key: 'value' }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                cargarUsuarios(); // Recargar la tabla después de eliminar
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error al eliminar usuario:', error);
            alert('Ocurrió un error al intentar eliminar el usuario.');
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