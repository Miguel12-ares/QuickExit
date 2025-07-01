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
        confirmarAccion(mensaje, function() {
          // Si el usuario confirma, se permite el envío del formulario
          // Puedes agregar aquí la lógica para enviar el formulario
        });
      });
    });
  });
  
function confirmarAccion(mensaje, onConfirm) {
    QuickExitNotifications.show({
        type: 'warning',
        title: 'Primera Confirmación',
        message: mensaje,
        duration: 0,
        dismissible: true,
        actions: [
            {
                text: 'Cancelar',
                type: 'secondary',
                icon: 'fas fa-times',
                callback: () => {}
            },
            {
                text: 'Continuar',
                type: 'primary',
                icon: 'fas fa-arrow-right',
                callback: () => {
                    QuickExitNotifications.show({
                        type: 'danger',
                        title: 'Confirmación Final',
                        message: '¿Estás completamente seguro?',
                        duration: 0,
                        dismissible: true,
                        actions: [
                            {
                                text: 'Cancelar',
                                type: 'secondary',
                                icon: 'fas fa-times',
                                callback: () => {}
                            },
                            {
                                text: 'Confirmar',
                                type: 'primary',
                                icon: 'fas fa-check',
                                callback: () => {
                                    if (typeof onConfirm === 'function') onConfirm();
                                }
                            }
                        ]
                    });
                }
            }
        ]
    });
}
  