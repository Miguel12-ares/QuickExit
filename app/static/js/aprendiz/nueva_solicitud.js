document.addEventListener('DOMContentLoaded', function() {
    const tipoSalidaSelect = document.getElementById('tipo_salida');
    const horaReingresoInput = document.getElementById('hora_reingreso');
    const horaReingresoGroup = document.getElementById('hora-reingreso-group');

    function toggleHoraReingreso() {
        if (!tipoSalidaSelect || !horaReingresoGroup || !horaReingresoInput) return;
        
        const selectedOption = tipoSalidaSelect.options[tipoSalidaSelect.selectedIndex];
        const tipoSalidaText = selectedOption.text.trim().toLowerCase();
        
        console.log(`Tipo de salida seleccionado: "${tipoSalidaText}"`);
        
        if (tipoSalidaText === 'definitiva') {
            // Limpiar clases de mostrar
            horaReingresoGroup.classList.remove('showing');
            
            // Iniciar animación de ocultación
            horaReingresoGroup.classList.add('hiding');
            
            // Limpiar el valor y quitar required
            horaReingresoInput.value = '';
            horaReingresoInput.removeAttribute('required');
            
            // Ocultar completamente después de la animación
            setTimeout(() => {
                if (horaReingresoGroup.classList.contains('hiding')) {
                    horaReingresoGroup.classList.add('hidden');
                }
            }, 400); // Duración de la transición CSS
            
            console.log('✅ Campo de hora de reingreso ocultándose para salida definitiva');
            
        } else if (tipoSalidaText === 'temporal' || (tipoSalidaText !== '' && tipoSalidaText !== 'definitiva')) {
            // Verificar si necesita animación de aparición
            const needsAnimation = horaReingresoGroup.classList.contains('hidden') || 
                                 horaReingresoGroup.classList.contains('hiding');
            
            if (needsAnimation) {
                // Limpiar clases de ocultar
                horaReingresoGroup.classList.remove('hiding', 'hidden');
                
                // Iniciar desde estado oculto para animar
                horaReingresoGroup.style.opacity = '0';
                horaReingresoGroup.style.maxHeight = '0';
                horaReingresoGroup.style.marginBottom = '0';
                horaReingresoGroup.style.transform = 'scaleY(0.8)';
                
                // Forzar un reflow para que los cambios se apliquen
                horaReingresoGroup.offsetHeight;
                
                // Usar requestAnimationFrame para la animación de aparición
                requestAnimationFrame(() => {
                    horaReingresoGroup.classList.add('showing');
                    
                    // Limpiar estilos inline para que CSS tome control
                    setTimeout(() => {
                        horaReingresoGroup.style.opacity = '';
                        horaReingresoGroup.style.maxHeight = '';
                        horaReingresoGroup.style.marginBottom = '';
                        horaReingresoGroup.style.transform = '';
                    }, 50);
                });
                
                console.log('✅ Campo de hora de reingreso apareciendo con animación para salida temporal');
            } else {
                // Si ya está visible, solo asegurar que tenga la clase showing
                horaReingresoGroup.classList.add('showing');
                console.log('✅ Campo de hora de reingreso ya visible para salida temporal');
            }
            
        } else {
            // Estado inicial - mostrar sin animación especial
            horaReingresoGroup.classList.remove('hiding', 'hidden');
            horaReingresoGroup.classList.add('showing');
            horaReingresoInput.removeAttribute('required');
            
            console.log('ℹ️ Estado inicial - campo de hora de reingreso visible');
        }
    }

    // Agregar event listener si los elementos existen
    if (tipoSalidaSelect && horaReingresoGroup) {
        tipoSalidaSelect.addEventListener('change', toggleHoraReingreso);
        
        // Ejecutar la función al cargar la página para manejar el estado inicial
        // Usar setTimeout para asegurar que el DOM esté completamente listo
        setTimeout(toggleHoraReingreso, 100);
        
        console.log('🚀 Event listener para tipo de salida configurado');
    } else {
        console.warn('⚠️ No se pudieron encontrar los elementos necesarios para la funcionalidad de hora de reingreso');
    }

    // Lógica para Motivo de la Solicitud
    const motivoPredeterminadoSelect = document.getElementById('motivo_predeterminado');
    const motivoEspecificacionGroup = document.getElementById('motivo_especificacion_group');
    const motivoEspecificacionInput = document.getElementById('motivo_especificacion');
    const formNuevaSolicitud = document.querySelector('.register-form');

    function toggleMotivoEspecificacion() {
        if (!motivoPredeterminadoSelect || !motivoEspecificacionGroup || !motivoEspecificacionInput) return;
        
        if (motivoPredeterminadoSelect.value === 'Otro') {
            motivoEspecificacionGroup.style.display = 'block';
            motivoEspecificacionInput.setAttribute('required', 'true');
            console.log('📝 Campo de especificación de motivo mostrado');
        } else {
            motivoEspecificacionGroup.style.display = 'none';
            motivoEspecificacionInput.removeAttribute('required');
            motivoEspecificacionInput.value = ''; // Limpiar el valor si no es 'Otro'
            console.log('📝 Campo de especificación de motivo ocultado');
        }
    }

    if (motivoPredeterminadoSelect && motivoEspecificacionGroup && motivoEspecificacionInput) {
        motivoPredeterminadoSelect.addEventListener('change', toggleMotivoEspecificacion);
        // Ejecutar la función al cargar la página para manejar el estado inicial
        toggleMotivoEspecificacion();
        console.log('🚀 Event listener para motivo configurado');
    }

    // Concatenar el motivo antes de enviar el formulario
    if (formNuevaSolicitud) {
        formNuevaSolicitud.addEventListener('submit', function(event) {
            if (!motivoPredeterminadoSelect || !motivoEspecificacionInput) return;
            
            const motivoPrincipal = motivoPredeterminadoSelect.value;
            const motivoEspecificacion = motivoEspecificacionInput.value.trim();
            let motivoFinal = motivoPrincipal;

            if (motivoPrincipal === 'Otro' && motivoEspecificacion === '') {
                event.preventDefault(); // Detener el envío si 'Otro' está seleccionado y la especificación está vacía
                showWarning('Por favor, especifique el motivo cuando selecciona "Otro".');
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
            
            console.log(`📤 Formulario enviado con motivo: "${motivoFinal}"`);
        });
        
        console.log('🚀 Event listener para envío de formulario configurado');
    }
    
    console.log('✅ Nueva Solicitud JS inicializado correctamente');
}); 