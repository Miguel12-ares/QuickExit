document.addEventListener('DOMContentLoaded', function() {
    const inputBuscar = document.querySelector('input[name="buscar_id"]');
    const inputNombre = document.querySelector('input[name="buscar_nombre"]');
    const inputInstructor = document.querySelector('input[name="buscar_instructor"]');
    const tablaBody = document.querySelector('.fichas-table tbody');
    const btnBuscar = document.getElementById('btn-buscar');
    const btnLimpiar = document.getElementById('btn-limpiar');
    const modalsContainer = document.getElementById('modals-container');

    let routeAsignar = document.querySelector('meta[name="route-asignar"]').content;
    let routeRemover = document.querySelector('meta[name="route-remover"]').content;

    let instructoresList = [];

    // Cargar instructores al inicio
    function cargarInstructores() {
        fetch('/api/buscar_instructores')
            .then(r => r.json())
            .then(d => {
                if (d.instructores) instructoresList = d.instructores;
            });
    }

    cargarInstructores();

    // Debounce para evitar demasiadas peticiones
    let debounceTimeout = null;
    function debounceBuscarFichas() {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(buscarFichas, 250);
    }

    // Función para renderizar las filas de la tabla
    function renderFichas(fichas) {
        tablaBody.innerHTML = '';
        modalsContainer.innerHTML = ''; // Limpiar modales existentes
        if (fichas.length === 0) {
            tablaBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No se encontraron resultados</td></tr>';
            return;
        }
        fichas.forEach(ficha => {
            const tieneInstructorLider = ficha.instructor_lider && ficha.instructor_lider !== 'Sin asignar';
            
            let accionesHtml = '';
            if (tieneInstructorLider) {
                accionesHtml = `
                    <button type="button" class="btn-lider" onclick="abrirModal('modal-${ficha.id_ficha}')">
                      <i class="fas fa-exchange-alt"></i> Cambiar Instructor
                    </button>
                    <form action="${routeRemover}${ficha.id_ficha}" method="POST" style="display:inline-block;">
                      <button type="submit" class="btn-remover">
                        <i class="fas fa-user-minus"></i> Remover
                      </button>
                    </form>
                `;
            } else {
                accionesHtml = `
                    <button type="button" class="btn-asignar" onclick="abrirModal('modal-${ficha.id_ficha}')">
                      <i class="fas fa-user-plus"></i> Asignar Instructor
                    </button>
                `;
            }

            tablaBody.innerHTML += `
                <tr>
                    <td>${ficha.id_ficha}</td>
                    <td>${ficha.nombre}</td>
                    <td>
                        ${tieneInstructorLider ? 
                            `<span class="badge-lider"><i class="fas fa-check-circle"></i> ${ficha.instructor_lider}</span>` :
                            `<span class="badge-sin-lider"><i class="fas fa-times-circle"></i> Sin instructor líder asignado</span>`
                        }
                    </td>
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
                    <td>${accionesHtml}</td>
                    <td>${ficha.descripcion}</td>
                </tr>
            `;

            // Generar modal para cada ficha
            modalsContainer.innerHTML += `
                <div id="modal-${ficha.id_ficha}" class="modal-overlay">
                    <div class="modal-container">
                        <div class="modal-header">
                            <i class="fas fa-user-plus"></i>
                            <h3>${tieneInstructorLider ? 'Cambiar' : 'Asignar'} Instructor Líder - ${ficha.nombre}</h3>
                        </div>
                        <form action="${routeAsignar}${ficha.id_ficha}" method="POST">
                            <div class="modal-body">
                                <select name="id_instructor" required>
                                    <option value="">Seleccione un instructor...</option>
                                    ${instructoresList.map(instructor => `
                                        <option value="${instructor.id_usuario}" ${ficha.id_instructor_lider == instructor.id_usuario ? 'selected' : ''}>
                                            ${instructor.nombre}
                                        </option>
                                    `).join('')}
                                </select>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="modal-btn btn-secondary" onclick="cerrarModal('modal-${ficha.id_ficha}')">
                                    <i class="fas fa-times"></i> Cancelar
                                </button>
                                <button type="submit" class="modal-btn">
                                    <i class="fas fa-check"></i> ${tieneInstructorLider ? 'Cambiar' : 'Asignar'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
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
