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
