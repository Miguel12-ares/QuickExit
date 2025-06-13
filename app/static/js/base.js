// static/js/base.js
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.getElementById('hamburger');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const body = document.body;

    // Verificar que todos los elementos existan
    if (!hamburger || !sidebar || !overlay) return;

    function toggleMenu() {
        hamburger.classList.toggle('active');
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
        body.classList.toggle('menu-open');
        body.style.overflow = sidebar.classList.contains('active') ? 'hidden' : '';
    }

    // Eventos para el botón hamburguesa
    hamburger.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        toggleMenu();
    });
    
    // Eventos para el overlay
    overlay.addEventListener('click', function(e) {
        e.preventDefault();
        toggleMenu();
    });

    // Cerrar menú al hacer clic en un enlace
    sidebar.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            if (sidebar.classList.contains('active')) {
                toggleMenu();
            }
        });
    });

    // Cerrar menú al redimensionar la ventana
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768 && sidebar.classList.contains('active')) {
            toggleMenu();
        }
    });

    // Prevenir que el menú se cierre al hacer clic dentro de él
    sidebar.addEventListener('click', function(e) {
        e.stopPropagation();
    });
});
