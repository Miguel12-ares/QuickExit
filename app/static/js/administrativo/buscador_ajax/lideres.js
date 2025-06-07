document.addEventListener('DOMContentLoaded', () => {
  const inputId = document.querySelector('input[name="buscar_id"]');
  const inputFicha = document.querySelector('input[name="buscar_ficha"]');
  const inputInstructor = document.querySelector('input[name="buscar_instructor"]');
  const selectEstado = document.querySelector('select[name="buscar_estado"]');
  const btnBuscar = document.getElementById('btn-buscar-lider');
  const btnLimpiar = document.getElementById('btn-limpiar-lider');
  const tbody = document.getElementById('tbody-lideres');

  let t;
  const debounce = fn => {
    clearTimeout(t);
    t = setTimeout(fn, 250);
  };

  function render(fichas) {
    tbody.innerHTML = '';
    if (fichas.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No se encontraron resultados</td></tr>';
      return;
    }
    fichas.forEach(ficha => {
      tbody.innerHTML += `
        <tr>
          <td>${ficha.id_ficha}</td>
          <td>${ficha.nombre}</td>
          <td>
            ${ficha.instructor_lider ? `<span class='badge-lider'>${ficha.instructor_lider}</span>` : `<span class='badge-sin-lider'>Sin instructor líder asignado</span>`}
          </td>
          <td>
            <div style="margin-bottom: 6px;">
              ${ficha.instructor_lider ? `
                <button type='button' class='btn-lider'>Cambiar Instructor</button>
                <form action='/admin/remover_instructor_lider/${ficha.id_ficha}' method='POST' style='display:inline-block;'>
                  <button type='submit' class='btn-remover'>Remover</button>
                </form>
              ` : `
                <button type='button' class='btn-asignar'>Asignar Instructor</button>
              `}
            </div>
          </td>
        </tr>
      `;
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