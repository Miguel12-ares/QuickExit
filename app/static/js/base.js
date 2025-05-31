// static/js/base.js
document.addEventListener("DOMContentLoaded", function() {
  var hamburger = document.getElementById("hamburger");
  var sidebar = document.getElementById("sidebar");

  if (hamburger && sidebar) {
      // Asegura que el sidebar esté oculto al inicio
      sidebar.classList.remove("active");

      hamburger.addEventListener("click", function() {
          sidebar.classList.toggle("active");
      });

      // Cierra el menú al hacer clic fuera del sidebar 
      document.addEventListener("click", function(e) {
        if (
          sidebar.classList.contains("active") &&
          !sidebar.contains(e.target) &&
          !hamburger.contains(e.target)
        ) {
          sidebar.classList.remove("active");
        }
      });
  }
});
