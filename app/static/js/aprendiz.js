// static/js/aprendiz.js

document.addEventListener("DOMContentLoaded", function() {
    var tipoSelect = document.getElementById("tipo_salida");
    var grupoReingreso = document.getElementById("grupoReingreso");
    var inputReingreso = document.getElementById("hora_reingreso");
  
    function toggleReingreso() {
      var selectedOption = tipoSelect.options[tipoSelect.selectedIndex];
      if (selectedOption.dataset.reingreso === "1") {
        grupoReingreso.style.display = "block";
        inputReingreso.required = true;
      } else {
        grupoReingreso.style.display = "none";
        inputReingreso.required = false;
      }
    }
  
    // Ejecutar al cargar la página
    toggleReingreso();
  
    // Escuchar cambios en el selector de tipo de salida
    tipoSelect.addEventListener("change", toggleReingreso);
  });
  