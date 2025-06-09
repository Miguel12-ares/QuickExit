document.addEventListener('DOMContentLoaded', function() {
    const inputBuscar = document.querySelector('input[name="buscar_id"]');
    const inputNombre = document.querySelector('input[name="buscar_nombre"]');
    const inputInstructor = document.querySelector('input[name="buscar_instructor"]');
    const tablaBody = document.querySelector('.fichas-table tbody');
    const btnBuscar = document.getElementById('btn-buscar');
    const btnLimpiar = document.getElementById('btn-limpiar');

    // Debounce para evitar demasiadas peticiones
    let debounceTimeout = null;
    function debounceBuscarFichas() {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(buscarFichas, 250);
    }

    // Función para renderizar las filas de la tabla
    function renderFichas(fichas) {
        tablaBody.innerHTML = '';
        if (fichas.length === 0) {
            tablaBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No se encontraron resultados</td></tr>';
            return;
        }
        fichas.forEach(ficha => {
            tablaBody.innerHTML += `
                <tr>
                    <td>${ficha.id_ficha}</td>
                    <td>${ficha.nombre}</td>
                    <td>${ficha.instructor_lider}</td>
                    <td>${ficha.fecha_creacion}</td>
                    <td>
                        <form method="POST" class="estado-form">
                            <input type="hidden" name="id_ficha" value="${ficha.id_ficha}">
                            <select name="nuevo_estado" class="estado-select">
                                <option value="activa" ${ficha.habilitada ? 'selected' : ''}>
                                    <i class="fas fa-check-circle"></i> Activa
                                </option>
                                <option value="deshabilitada" ${!ficha.habilitada ? 'selected' : ''}>
                                    <i class="fas fa-times-circle"></i> Deshabilitada
                                </option>
                            </select>
                            <button type="submit" class="btn-estado">
                                <i class="fas fa-save"></i> Guardar
                            </button>
                        </form>
                    </td>
                    <td>${ficha.descripcion}</td>
                </tr>
            `;
        });
    }

    // Función para hacer la búsqueda AJAX
    function buscarFichas() {
        const params = new URLSearchParams();
        if (inputBuscar.value.trim() !== '') params.append('buscar_id', inputBuscar.value.trim());
        if (inputNombre.value.trim() !== '') params.append('buscar_nombre', inputNombre.value.trim());
        if (inputInstructor.value.trim() !== '') params.append('buscar_instructor', inputInstructor.value.trim());
        fetch(`/api/buscar_fichas?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                if (data.fichas) {
                    renderFichas(data.fichas);
                }
            });
    }

    // Event listeners
    inputBuscar.addEventListener('input', debounceBuscarFichas);
    inputNombre.addEventListener('input', debounceBuscarFichas);
    inputInstructor.addEventListener('input', debounceBuscarFichas);
    
    btnBuscar.addEventListener('click', buscarFichas);
    btnLimpiar.addEventListener('click', function() {
        inputBuscar.value = '';
        inputNombre.value = '';
        inputInstructor.value = '';
        buscarFichas();
    });

    // Búsqueda inicial
    buscarFichas();
});
