document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('noFichasModal');
    console.log('Estado del modal:', modal.dataset.show); // Debug

    // Verificar si hay un mensaje de "no fichas asignadas" en el data attribute
    if (modal.dataset.show === 'true') {
        // Retrasar la aparición del modal por 500ms para permitir que la tabla se anime primero
        setTimeout(() => {
            modal.style.display = 'block';
        }, 500);
    }

    // Manejar el clic en el botón del modal
    document.querySelector('.modal-btn').addEventListener('click', function() {
        window.location.href = this.dataset.url;
    });
}); 