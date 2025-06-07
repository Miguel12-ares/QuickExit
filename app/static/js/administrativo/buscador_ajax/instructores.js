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
});