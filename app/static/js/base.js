// static/js/base.js
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.getElementById('hamburger');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const body = document.body;

    // Verificar que todos los elementos existan
    if (!hamburger || !sidebar || !overlay) {
        console.error('Elementos del menú no encontrados');
        return;
    }

    function toggleMenu() {
        hamburger.classList.toggle('active');
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
        body.classList.toggle('menu-open');
        body.style.overflow = sidebar.classList.contains('active') ? 'hidden' : '';
    }

    // Eventos para el botón hamburguesa
    ['click', 'touchend'].forEach(eventType => {
        hamburger.addEventListener(eventType, function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleMenu();
        }, { passive: false });
    });
    
    // Eventos para el overlay
    ['click', 'touchend'].forEach(eventType => {
        overlay.addEventListener(eventType, function(e) {
            e.preventDefault();
            toggleMenu();
        }, { passive: false });
    });

    // Cerrar menú al hacer clic en un enlace
    const menuLinks = sidebar.querySelectorAll('a');
    menuLinks.forEach(link => {
        ['click', 'touchend'].forEach(eventType => {
            link.addEventListener(eventType, () => {
                if (sidebar.classList.contains('active')) {
                    toggleMenu();
                }
            }, { passive: true });
        });
    });

    // Cerrar menú al redimensionar la ventana
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768 && sidebar.classList.contains('active')) {
            toggleMenu();
        }
    });

    // Asegurar que el menú esté cerrado al cargar la página
    if (sidebar.classList.contains('active')) {
        toggleMenu();
    }
    
    // Prevenir que el menú se cierre al hacer clic dentro de él
    ['click', 'touchend'].forEach(eventType => {
        sidebar.addEventListener(eventType, function(e) {
            e.stopPropagation();
        });
    });
    
    // Fix para iOS: asegurar que el scroll funcione correctamente
    sidebar.addEventListener('touchmove', function(e) {
        e.stopPropagation();
    }, { passive: true });
});
