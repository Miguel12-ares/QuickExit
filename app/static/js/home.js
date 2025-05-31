// Animaciones suaves al cargar para la página de inicio

document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.animate-fade-in').forEach(el => {
    el.classList.add('visible');
  });
  setTimeout(() => {
    document.querySelectorAll('.animate-fade-in-delay').forEach(el => {
      el.classList.add('visible');
    });
  }, 300);
  setTimeout(() => {
    document.querySelectorAll('.animate-pop-in').forEach(el => {
      el.classList.add('visible');
    });
  }, 600);
  setTimeout(() => {
    document.querySelectorAll('.animate-slide-down').forEach(el => {
      el.classList.add('visible');
    });
  }, 100);
}); 