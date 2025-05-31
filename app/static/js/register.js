// static/js/register.js

document.addEventListener("DOMContentLoaded", function() {
    var rol = document.getElementById("rol");
    var fichaContainer = document.getElementById("ficha-container");
  
    function toggleFicha() {
      // Muestra "ficha-container" solo si el rol es "aprendiz"
      if (rol.value === "aprendiz") {
        fichaContainer.style.display = "block";
      } else {
        fichaContainer.style.display = "none";
      }
    }
  
    // Ejecutar al cargar la página (por si "Aprendiz" está seleccionado por defecto)
    toggleFicha();
  
    // Escuchar cambios en el selector de rol
    rol.addEventListener("change", toggleFicha);
  });
  