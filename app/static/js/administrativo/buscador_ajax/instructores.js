document.addEventListener('DOMContentLoaded', () => {
  const inputId = document.querySelector('input[name="buscar_id"]');
  const inputNombre = document.querySelector('input[name="buscar_nombre"]');
  const inputEmail = document.querySelector('input[name="buscar_email"]');
  const btnBuscar = document.getElementById('btn-buscar-inst');
  const btnLimpiar = document.getElementById('btn-limpiar-inst');
  const tbody = document.querySelector('.instructores-table tbody');

  let t;
  const debounce = fn => {
    clearTimeout(t);
    t = setTimeout(fn, 250);
  };

  function render(instructores) {
    tbody.innerHTML = '';
    if (instructores.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No se encontraron resultados</td></tr>';
      return;
    }
    instructores.forEach(i => {
      tbody.innerHTML += `
        <tr>
          <td>${i.id_usuario}</td>
          <td>${i.nombre}</td>
          <td>${i.email}</td>
          <td>${i.ficha_nombre ? i.ficha_nombre : '-'}</td>
          <td>${i.validado ? 'Validado' : 'Pendiente'}</td>
        </tr>`;
    });
  }

  function buscarInstructores() {
    const params = new URLSearchParams();
    if (inputId.value.trim() !== '') params.append('buscar_id', inputId.value.trim());
    if (inputNombre.value.trim() !== '') params.append('buscar_nombre', inputNombre.value.trim());
    if (inputEmail.value.trim() !== '') params.append('buscar_email', inputEmail.value.trim());
    fetch(`/admin/api/buscar_instructores?${params.toString()}`)
      .then(response => response.json())
      .then(data => {
        if (data.instructores) {
          render(data.instructores);
        } else {
          tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No se encontraron resultados</td></tr>';
        }
      })
      .catch(error => {
        console.error('Error al buscar instructores:', error);
      });
  }

  inputId.addEventListener('input', () => debounce(buscarInstructores));
  inputNombre.addEventListener('input', () => debounce(buscarInstructores));
  inputEmail.addEventListener('input', () => debounce(buscarInstructores));
  btnBuscar.addEventListener('click', buscarInstructores);
  btnLimpiar.addEventListener('click', function() {
    inputId.value = '';
    inputNombre.value = '';
    inputEmail.value = '';
    buscarInstructores();
  });

  // Búsqueda inicial
  buscarInstructores();
});