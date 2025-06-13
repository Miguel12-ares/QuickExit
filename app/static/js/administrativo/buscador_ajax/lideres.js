document.addEventListener('DOMContentLoaded', () => {
  const inputId = document.querySelector('input[name="buscar_id"]');
  const inputFicha = document.querySelector('input[name="buscar_ficha"]');
  const inputInstructor = document.querySelector('input[name="buscar_instructor"]');
  const selectEstado = document.querySelector('select[name="buscar_estado"]');
  const btnBuscar = document.getElementById('btn-buscar-lider');
  const btnLimpiar = document.getElementById('btn-limpiar-lider');
  const tbody = document.getElementById('tbody-lideres');

  // Obtener las rutas correctas desde el HTML
  const routeAsignar = document.querySelector('meta[name="route-asignar"]')?.content || '/admin/asignar_instructor_lider/';
  const routeRemover = document.querySelector('meta[name="route-remover"]')?.content || '/admin/remover_instructor_lider/';

  let t;
  const debounce = fn => {
    clearTimeout(t);
    t = setTimeout(fn, 250);
  };

  // Función para mostrar/ocultar botones cuando se abre/cierra el modal
  function toggleBotones(fichaId, mostrar) {
    const modal = document.getElementById(`modal-${fichaId}`);
    const celda = modal.closest('td');
    const botones = celda.querySelector('div');
    
    if (mostrar) {
      botones.style.display = 'flex';
      modal.style.display = 'none';
    } else {
      botones.style.display = 'none';
      modal.style.display = 'block';
    }
  }

  // Obtener la lista de instructores para los modales
  let instructoresList = [];
  function cargarInstructores() {
    fetch('/api/buscar_instructores')
      .then(r => r.json())
      .then(d => {
        if (d.instructores) instructoresList = d.instructores;
      });
  }
  
  // Cargar instructores al inicio
  cargarInstructores();

  // Función para cerrar modales (global)
  window.cerrarModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = 'none';
    }
  };

  // Función para abrir modales (global)
  window.abrirModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = 'block';
    }
  };

  function render(fichas) {
    tbody.innerHTML = '';
    if (fichas.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No se encontraron resultados</td></tr>';
      return;
    }
    
    fichas.forEach(ficha => {
      // Crear la fila con innerHTML para mayor simplicidad
      const row = document.createElement('tr');
      
      // Columna ID
      row.innerHTML += `<td>${ficha.id_ficha}</td>`;
      
      // Columna Nombre
      row.innerHTML += `<td>${ficha.nombre}</td>`;
      
      // Columna Instructor Líder
      if (ficha.instructor_lider) {
        row.innerHTML += `
          <td>
            <span class="badge-lider"><i class="fas fa-check-circle"></i> ${ficha.instructor_lider}</span>
          </td>`;
      } else {
        row.innerHTML += `
          <td>
            <span class="badge-sin-lider"><i class="fas fa-times-circle"></i> Sin instructor líder asignado</span>
          </td>`;
      }
      
      // Columna Acciones
      const modalId = `modal-${ficha.id_ficha}`;
      
      // Crear la celda de acciones
      const tdAcciones = document.createElement('td');
      
      // Contenedor de botones
      const divBotones = document.createElement('div');
      divBotones.className = 'botones-container';
      
      if (ficha.instructor_lider) {
        // Botón Cambiar Instructor
        divBotones.innerHTML = `
          <button type="button" class="btn-lider" onclick="abrirModal('${modalId}')">
            <i class="fas fa-exchange-alt"></i> Cambiar Instructor
          </button>
          <form action="${routeRemover}${ficha.id_ficha}" method="POST" style="display:inline-block;">
            <button type="submit" class="btn-remover">
              <i class="fas fa-user-minus"></i> Remover
            </button>
          </form>
        `;
      } else {
        // Botón Asignar Instructor
        divBotones.innerHTML = `
          <button type="button" class="btn-asignar" onclick="abrirModal('${modalId}')">
            <i class="fas fa-user-plus"></i> Asignar Instructor
          </button>
        `;
      }
      
      tdAcciones.appendChild(divBotones);
      row.appendChild(tdAcciones);
      tbody.appendChild(row);
    });

    // Crear los modales fuera de la tabla
    crearModales(fichas);
  }

  // Función para crear los modales
  function crearModales(fichas) {
    // Limpiar modales existentes
    document.querySelectorAll('.modal-overlay').forEach(modal => modal.remove());
    
    fichas.forEach(ficha => {
      const modalId = `modal-${ficha.id_ficha}`;
      
      // Crear el contenido del modal
      let instructoresOptions = '<option value="">Seleccione un instructor...</option>';
      instructoresList.forEach(instructor => {
        const selected = ficha.id_instructor_lider && ficha.id_instructor_lider == instructor.id_usuario ? 'selected' : '';
        instructoresOptions += `<option value="${instructor.id_usuario}" ${selected}>${instructor.nombre}</option>`;
      });
      
      // Crear el modal
      const modalHTML = `
        <div id="${modalId}" class="modal-overlay">
          <div class="modal-container">
            <div class="modal-header">
              <i class="fas fa-user-plus"></i>
              <h3>Asignar Instructor Líder - ${ficha.nombre}</h3>
            </div>
            <form action="${routeAsignar}${ficha.id_ficha}" method="POST">
              <div class="modal-body">
                <select name="id_instructor" required>
                  ${instructoresOptions}
                </select>
              </div>
              <div class="modal-footer">
                <button type="button" class="modal-btn btn-secondary" onclick="cerrarModal('${modalId}')">
                  <i class="fas fa-times"></i> Cancelar
                </button>
                <button type="submit" class="modal-btn">
                  <i class="fas fa-check"></i> Asignar
                </button>
              </div>
            </form>
          </div>
        </div>
      `;
      
      // Añadir al final del body
      document.body.insertAdjacentHTML('beforeend', modalHTML);
    });
  }

  function buscar() {
    const params = new URLSearchParams();
    if (inputId.value.trim()) params.append('buscar_id', inputId.value.trim());
    if (inputFicha.value.trim()) params.append('buscar_ficha', inputFicha.value.trim());
    if (inputInstructor.value.trim()) params.append('buscar_instructor', inputInstructor.value.trim());
    if (selectEstado.value) params.append('buscar_estado', selectEstado.value);
    fetch(`/api/buscar_fichas_lideres?${params.toString()}`)
      .then(r => r.json())
      .then(d => {
        if (d.fichas) render(d.fichas);
      });
  }

  [inputId, inputFicha, inputInstructor, selectEstado].forEach(i => {
    i.addEventListener('keyup', () => debounce(buscar));
    i.addEventListener('change', buscar);
    i.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); buscar(); }
    });
  });

  btnBuscar.addEventListener('click', buscar);
  btnLimpiar.addEventListener('click', () => {
    inputId.value = inputFicha.value = inputInstructor.value = '';
    selectEstado.value = '';
    buscar();
  });

  // inicial
  buscar();
}); 