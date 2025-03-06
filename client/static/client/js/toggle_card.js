document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("toggleModules");
    const moduleList = document.getElementById("moduleList");
    const hiddenModules = document.querySelectorAll(".hidden-module");
    let isExpanded = false;

    if (toggleButton) {
        toggleButton.addEventListener("click", function () {
            isExpanded = !isExpanded;

            hiddenModules.forEach(module => {
                module.style.display = isExpanded ? "flex" : "none";
            });

            toggleButton.textContent = isExpanded ? "View Less" : "View All";
        });
    }
});
