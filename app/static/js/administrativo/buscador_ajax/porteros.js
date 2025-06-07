document.addEventListener('DOMContentLoaded', () => {
  const inputIdent = document.querySelector('input[name="buscar_identificacion"]');
  const inputNombre = document.querySelector('input[name="buscar_nombre"]');
  const inputEmail = document.querySelector('input[name="buscar_email"]');
  const btnBuscar = document.getElementById('btn-buscar-port');
  const btnLimpiar = document.getElementById('btn-limpiar-port');
  const tbody = document.querySelector('.porteros-table tbody');

  let t;
  const debounce = fn => {
    clearTimeout(t);
    t = setTimeout(fn, 250);
  };

  function render(porteros) {
    tbody.innerHTML = '';
    if (porteros.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No se encontraron resultados</td></tr>';
      return;
    }
    porteros.forEach(p => {
      tbody.innerHTML += `
        <tr>
          <td>${p.documento}</td>
          <td>${p.nombre}</td>
          <td>${p.email}</td>
          <td>
            <form action="/admin/actualizar_estado_portero/${p.id_usuario}" method="post" style="display:inline;">
              <select name="validado" class="estado-select${!p.validado ? ' desactivado' : ''}" onchange="this.form.submit()">
                <option value="true" ${p.validado ? 'selected' : ''}>Activo</option>
                <option value="false" ${!p.validado ? 'selected' : ''}>Desactivado</option>
              </select>
            </form>
          </td>
        </tr>`;
    });
  }

  function buscar() {
    const params = new URLSearchParams();
    if (inputIdent.value.trim()) params.append('buscar_identificacion', inputIdent.value.trim());
    if (inputNombre.value.trim()) params.append('buscar_nombre', inputNombre.value.trim());
    if (inputEmail.value.trim()) params.append('buscar_email', inputEmail.value.trim());
    fetch(`/api/buscar_porteros?${params.toString()}`)
      .then(r => r.json())
      .then(d => {
        if (d.porteros) render(d.porteros);
      });
  }

  [inputIdent, inputNombre, inputEmail].forEach(i => {
    i.addEventListener('keyup', () => debounce(buscar));
    i.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); buscar(); }
    });
  });

  btnBuscar.addEventListener('click', buscar);
  btnLimpiar.addEventListener('click', () => {
    inputIdent.value = inputNombre.value = inputEmail.value = '';
    buscar();
  });

  // inicial
  buscar();
}); 