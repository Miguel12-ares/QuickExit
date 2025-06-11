document.addEventListener('DOMContentLoaded', function() {
    const tipoSalidaSelect = document.getElementById('tipo_salida');
    const horaReingresoGroup = document.querySelector('.form-group:has(#hora_reingreso)');

    function toggleHoraReingreso() {
        const selectedOption = tipoSalidaSelect.options[tipoSalidaSelect.selectedIndex];
        const tipoSalidaText = selectedOption.text.trim().toLowerCase();
        
        if (tipoSalidaText === 'definitiva') {
            horaReingresoGroup.style.opacity = '0';
            horaReingresoGroup.style.height = '0';
            horaReingresoGroup.style.margin = '0';
            horaReingresoGroup.style.overflow = 'hidden';
            horaReingresoGroup.style.transition = 'all 0.3s ease-in-out';
            document.getElementById('hora_reingreso').value = '';
        } else {
            horaReingresoGroup.style.opacity = '1';
            horaReingresoGroup.style.height = 'auto';
            horaReingresoGroup.style.marginBottom = '1.5rem'; /* Ajustado para el nuevo estilo */
            horaReingresoGroup.style.overflow = 'visible';
            horaReingresoGroup.style.transition = 'all 0.3s ease-in-out';
        }
    }

    if (tipoSalidaSelect && horaReingresoGroup) {
        tipoSalidaSelect.addEventListener('change', toggleHoraReingreso);
        // Ejecutar la función al cargar la página para manejar el estado inicial
        toggleHoraReingreso();
    }

    // Lógica para Motivo de la Solicitud
    const motivoPredeterminadoSelect = document.getElementById('motivo_predeterminado');
    const motivoEspecificacionGroup = document.getElementById('motivo_especificacion_group');
    const motivoEspecificacionInput = document.getElementById('motivo_especificacion');
    const formNuevaSolicitud = document.querySelector('.form-nueva-solicitud');

    function toggleMotivoEspecificacion() {
        if (motivoPredeterminadoSelect.value === 'Otro') {
            motivoEspecificacionGroup.style.display = 'block';
            motivoEspecificacionInput.setAttribute('required', 'true');
        } else {
            motivoEspecificacionGroup.style.display = 'none';
            motivoEspecificacionInput.removeAttribute('required');
            motivoEspecificacionInput.value = ''; // Limpiar el valor si no es 'Otro'
        }
    }

    if (motivoPredeterminadoSelect && motivoEspecificacionGroup && motivoEspecificacionInput) {
        motivoPredeterminadoSelect.addEventListener('change', toggleMotivoEspecificacion);
        // Ejecutar la función al cargar la página para manejar el estado inicial
        toggleMotivoEspecificacion();
    }

    // Concatenar el motivo antes de enviar el formulario
    if (formNuevaSolicitud) {
        formNuevaSolicitud.addEventListener('submit', function(event) {
            const motivoPrincipal = motivoPredeterminadoSelect.value;
            const motivoEspecificacion = motivoEspecificacionInput.value.trim();
            let motivoFinal = motivoPrincipal;

            if (motivoPrincipal === 'Otro' && motivoEspecificacion === '') {
                event.preventDefault(); // Detener el envío si 'Otro' está seleccionado y la especificación está vacía
                alert('Por favor, especifique el motivo cuando selecciona "Otro".');
                return;
            }

            if (motivoEspecificacion !== '' && motivoPrincipal !== 'Otro') {
                motivoFinal = `${motivoPrincipal}: ${motivoEspecificacion}`;
            } else if (motivoEspecificacion !== '' && motivoPrincipal === 'Otro') {
                motivoFinal = motivoEspecificacion;
            }

            // Crear un campo de entrada oculto para 'motivo' y adjuntarlo al formulario
            let hiddenMotivoInput = document.createElement('input');
            hiddenMotivoInput.type = 'hidden';
            hiddenMotivoInput.name = 'motivo';
            hiddenMotivoInput.value = motivoFinal;
            formNuevaSolicitud.appendChild(hiddenMotivoInput);
        });
    }
}); 