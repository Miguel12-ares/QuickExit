// static/js/instructor.js

document.addEventListener("DOMContentLoaded", function() {
    var actionForms = document.querySelectorAll(".action-form");
  
    actionForms.forEach(function(form) {
      form.addEventListener("submit", function(e) {
        // Obtener el botón que disparó el submit
        var btn = form.querySelector("button");
        var accion = btn.classList.contains("aprobar") ? "aprobar" : "rechazar";
        var mensaje = accion === "aprobar" ?
                      "¿Estás seguro de aprobar esta solicitud? Al aprobar, esta solicitud se enviará al área administrativa." :
                      "¿Estás seguro de rechazar esta solicitud?";
        if (!confirm(mensaje)) {
          e.preventDefault();
        }
      });
    });
  });
  