// static/js/admin_instructores.js

document.addEventListener("DOMContentLoaded", function() {
    var approveButtons = document.querySelectorAll(".btn.aprobar");
    var rejectButtons = document.querySelectorAll(".btn.rechazar");
  
    approveButtons.forEach(function(btn) {
      btn.addEventListener("click", function(e) {
        e.preventDefault();
      });
    });
  
    rejectButtons.forEach(function(btn) {
      btn.addEventListener("click", function(e) {
        e.preventDefault();
      });
    });
  });
  
function aprobarInstructor(id_instructor, nombre) {
    QuickExitNotifications.show({
        type: 'warning',
        title: 'Primera Confirmación',
        message: `¿Estás seguro de aprobar a ${nombre}?`,
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
                        type: 'success',
                        title: 'Confirmación Final',
                        message: `¿Realmente deseas aprobar a ${nombre}?`,
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
                                text: 'Aprobar',
                                type: 'primary',
                                icon: 'fas fa-check',
                                callback: () => {
                                    // Aquí va la lógica de aprobación
                                }
                            }
                        ]
                    });
                }
            }
        ]
    });
}

function rechazarInstructor(id_instructor, nombre) {
    QuickExitNotifications.show({
        type: 'warning',
        title: 'Primera Confirmación',
        message: `¿Estás seguro de rechazar a ${nombre}? Esta acción eliminará al usuario.`,
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
                        message: `¿Realmente deseas rechazar a ${nombre}? Esta acción eliminará al usuario permanentemente.`,
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
                                text: 'Rechazar',
                                type: 'primary',
                                icon: 'fas fa-trash',
                                callback: () => {
                                    // Aquí va la lógica de rechazo
                                }
                            }
                        ]
                    });
                }
            }
        ]
    });
}
  