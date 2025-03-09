document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("toggleModules");
    const moduleList = document.getElementById("moduleList");  // Main module container
    const hiddenModules = document.querySelectorAll(".hidden-module");

    if (!toggleButton || !moduleList) {
        return;  // Stop execution if elements don't exist
    }

    let isExpanded = false;

    toggleButton.addEventListener("click", function () {
        isExpanded = !isExpanded;

        hiddenModules.forEach(module => {
            module.style.display = isExpanded ? "flex" : "none";  // Ensure flex layout
        });

        toggleButton.textContent = isExpanded ? "View Less" : "View All";
    });
});


function toggleAnswers(questionnaireId) {
    let answersContainer = document.getElementById(`answers-${questionnaireId}`);
    let button = document.querySelector(`button[onclick="toggleAnswers('${questionnaireId}')"]`);

    if (answersContainer.classList.contains("hidden")) {
        answersContainer.classList.remove("hidden");
        button.innerText = "Hide Answers";
    } else {
        answersContainer.classList.add("hidden");
        button.innerText = "View Answers";
    }
}
