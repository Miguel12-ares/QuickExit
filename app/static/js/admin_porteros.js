// static/js/admin_porteros.js

document.addEventListener("DOMContentLoaded", function() {
    var approveButtons = document.querySelectorAll(".btn.aprobar");
    var rejectButtons = document.querySelectorAll(".btn.rechazar");
  
    approveButtons.forEach(function(btn) {
      btn.addEventListener("click", function(e) {
        if (!confirm("¿Estás seguro de aprobar este portero?")) {
          e.preventDefault();
        }
      });
    });
  
    rejectButtons.forEach(function(btn) {
      btn.addEventListener("click", function(e) {
        if (!confirm("¿Estás seguro de rechazar este portero? Esto eliminará al usuario.")) {
          e.preventDefault();
        }
      });
    });
  });
  