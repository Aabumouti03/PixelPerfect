function resetSearch() {
    document.getElementById("search").value = ""; // Clear search input
}

function resetFilters() {
    const form = document.getElementById("filterForm");

    document.getElementById("filter_type").value = "all";
    document.getElementById("sort").value = "";

    const categoryCheckboxes = document.querySelectorAll('.pill-checkbox[name="category"]');
    categoryCheckboxes.forEach(cb => cb.checked = true);

    // Sync visual state
    document.getElementById("category_all").checked = true;
    updatePillSelection();

    document.getElementById("search").value = "";

    form.submit();
}

function updatePillSelection() {
const allCheckbox = document.getElementById("category_all");
const allLabel = document.getElementById("all-label");
const categoryCheckboxes = document.querySelectorAll('.pill-checkbox[name="category"]');

const allSelected = Array.from(categoryCheckboxes).every(cb => cb.checked);

categoryCheckboxes.forEach(box => {
    const label = document.querySelector(`label[for="${box.id}"]`);
    label.classList.toggle("selected", false);
});

allLabel.classList.toggle("selected", allSelected);
allCheckbox.checked = allSelected;
}

document.addEventListener("DOMContentLoaded", function () {
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");
const programsUrl = document.querySelector('meta[name="programs-url"]').getAttribute("content");
const modulesUrl = document.querySelector('meta[name="modules-url"]').getAttribute("content");    
const allCheckbox = document.getElementById("category_all");
const categoryCheckboxes = document.querySelectorAll('.pill-checkbox[name="category"]');
const allLabel = document.getElementById("all-label");

// Mark all as selected on first load if nothing selected
const noneSelectedInitially = Array.from(categoryCheckboxes).every(cb => !cb.checked);
if (noneSelectedInitially) {
    categoryCheckboxes.forEach(cb => cb.checked = true);
}
updatePillSelection();

allCheckbox.addEventListener("change", () => {
    const isChecked = allCheckbox.checked;
    if (isChecked) {
        categoryCheckboxes.forEach(cb => cb.checked = true);
    }
    updatePillSelection();
});

categoryCheckboxes.forEach(box => {
    box.addEventListener("change", () => {
        updatePillSelection();
    });
});

    // Program Logic
    document.querySelectorAll(".enroll-button[data-program-id]").forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault(); // Prevent form submission or button default behavior

            const programId = this.dataset.programId;
            const isEnrolled = this.dataset.enrolled === "true";
            const action = isEnrolled ? "unenroll" : "enroll";

            // Deselect others
            document.querySelectorAll(".enroll-button[data-program-id]").forEach(b => {
                b.textContent = "Enroll";
                b.dataset.enrolled = "false";
                b.classList.remove("enrolled");
            });

            // Toggle this one visually
            if (!isEnrolled) {
                this.textContent = "Enrolled";
                this.dataset.enrolled = "true";
                this.classList.add("enrolled");
            }

            fetch(programsUrl, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({
                  program_id: programId,
                  action: action
                })
            });
        });
    });


// Module Logic
document.querySelectorAll(".enroll-button[data-module-id]").forEach(button => {
    button.addEventListener("click", function (e) {
        e.preventDefault(); // Stop default button action

        const moduleId = this.dataset.moduleId;
        const isEnrolled = this.dataset.enrolled === "true";
        const action = isEnrolled ? "unenroll" : "enroll";

        if (isEnrolled) {
            this.textContent = "Enroll";
            this.dataset.enrolled = "false";
            this.classList.remove("enrolled");
        } else {
            this.textContent = "Enrolled";
            this.dataset.enrolled = "true";
            this.classList.add("enrolled");
        }

        fetch(modulesUrl, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({
              module_id: moduleId,
              action: action
            })
        });
    });
});

});
// Logout Modal
const logoutBtn = document.getElementById("logout-btn");
const logoutModal = document.getElementById("logout-modal");
const cancelLogout = document.getElementById("cancel-logout");

logoutBtn.addEventListener("click", () => logoutModal.style.display = "block");
cancelLogout.addEventListener("click", () => logoutModal.style.display = "none");

window.onclick = function(event) {
if (event.target === logoutModal) {
    logoutModal.style.display = "none";
}
};
