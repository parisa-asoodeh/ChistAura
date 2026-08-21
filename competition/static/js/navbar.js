document.addEventListener("DOMContentLoaded", () => {

    const toggle = document.getElementById("navbar-toggle");
    const links = document.querySelector(".navbar-links");

    if (!toggle || !links) {
        return;
    }

    toggle.addEventListener("click", () => {

        links.classList.toggle("active");

        const isOpen = links.classList.contains("active");

        toggle.classList.toggle("is-open" , isOpen);

        toggle.setAttribute(
            "aria-expanded",
            isOpen
        );

    });

});