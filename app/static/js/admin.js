document.addEventListener("DOMContentLoaded", function() {
    var hamburger = document.getElementById("hamburger");
    var menu = document.getElementById("admin-menu");

    hamburger.addEventListener("click", function() {
        // Alterna la visibilidad del menú
        if (menu.style.display === "block") {
            menu.style.display = "none";
        } else {
            menu.style.display = "block";
        }
    });
});
