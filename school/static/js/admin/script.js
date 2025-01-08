document.addEventListener("DOMContentLoaded", function() {
    const menuToggle = document.getElementById("menu-toggle");
    const wrapper = document.getElementById("wrapper");

    menuToggle.addEventListener("click", function(e) {
        e.preventDefault();
        wrapper.classList.toggle("toggled");
    });

    // Adjust sidebar visibility based on screen size on load
    function checkScreenSize() {
        if (window.innerWidth >= 768) {
            wrapper.classList.remove("toggled");
        } else {
            wrapper.classList.add("toggled");
        }
    }

    // Check screen size on load
    checkScreenSize();

    // Add event listener for window resize
    window.addEventListener("resize", checkScreenSize);
});
