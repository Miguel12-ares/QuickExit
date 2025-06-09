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
            horaReingresoGroup.style.marginBottom = '1.2rem';
            horaReingresoGroup.style.overflow = 'visible';
            horaReingresoGroup.style.transition = 'all 0.3s ease-in-out';
        }
    }

    tipoSalidaSelect.addEventListener('change', toggleHoraReingreso);
    // Ejecutar la función al cargar la página para manejar el estado inicial
    toggleHoraReingreso();
}); 