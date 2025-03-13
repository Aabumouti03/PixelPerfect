document.addEventListener("DOMContentLoaded", function () {
    var availableModules = document.getElementById("availableModules");
    var sortableModules = document.getElementById("sortableModules");
    var moduleOrderInput = document.getElementById("module_order");
    var applyFilterBtn = document.getElementById("applyFilter");
    var selectAllCheckbox = document.getElementById("selectAllCategories");
    var form = document.querySelector("form");

    var sortable = new Sortable(sortableModules, {
        animation: 150,
        onEnd: function () {
            updateModuleNumbers();
            updateModuleOrderInput();
        }
    });

    
    form.addEventListener("submit", function (event) {
        updateModuleOrderInput();
        console.log("Final module_order before submit:", moduleOrderInput.value);

        if (!moduleOrderInput.value.trim()) {
            console.error("No module_order received! Check JavaScript.");
            alert("No module order detected. Please arrange modules before submitting.");
            event.preventDefault();
        }
    });

    // when a module is selected, add it to the sortable list
    availableModules.querySelectorAll("input[type='checkbox']").forEach(function (checkbox) {
        checkbox.addEventListener("change", function () {
            if (this.checked) {
                addModuleToSortableList(this.value, this.nextElementSibling.innerText);
            } else {
                removeModuleById(this.value);
            }
        });
    });

    // listen for remove button clicks in the sorted list
    sortableModules.addEventListener("click", function (event) {
        if (event.target.classList.contains("remove-module")) {
            var listItem = event.target.closest("li");
            var moduleId = listItem.dataset.moduleId;
            availableModules.querySelector(`input[value="${moduleId}"]`).checked = false;
            listItem.remove();
            updateModuleNumbers();
            updateModuleOrderInput();
        }
    });

    function addModuleToSortableList(moduleId, moduleTitle) {
        if (!sortableModules.querySelector(`li[data-module-id="${moduleId}"]`)) {
            var listItem = document.createElement("li");
            listItem.className = "d-flex align-items-center p-2 border rounded mb-2 sortable-item";
            listItem.dataset.moduleId = moduleId;
            listItem.innerHTML = `
                <span class="module-number me-2"></span>
                <span>${moduleTitle}</span>
                <button type="button" class="btn btn-sm btn-danger ms-auto remove-module">✖</button>
            `;

            sortableModules.appendChild(listItem);
            updateModuleNumbers();
            updateModuleOrderInput();
        }
    }

    function removeModuleById(moduleId) {
        var listItem = sortableModules.querySelector(`li[data-module-id="${moduleId}"]`);
        if (listItem) {
            listItem.remove();
            updateModuleNumbers();
            updateModuleOrderInput();
        }
    }

    function updateModuleNumbers() {
        sortableModules.querySelectorAll("li").forEach((item, index) => {
            item.querySelector(".module-number").textContent = (index + 1) + ".";
        });
    }

    function updateModuleOrderInput() {
        var order = [];
        sortableModules.querySelectorAll("li").forEach(item => {
            order.push(item.dataset.moduleId);
        });
        moduleOrderInput.value = order.join(",");
        console.log("Updated module_order:", moduleOrderInput.value);
    }

    selectAllCheckbox.addEventListener("change", function () {
        var categoryCheckboxes = document.querySelectorAll(".category-checkbox");
        categoryCheckboxes.forEach(checkbox => checkbox.checked = this.checked);

        if (!this.checked) {
            resetModuleDisplay();
        }
    });

    applyFilterBtn.addEventListener("click", function () {
        var selectedCategories = Array.from(document.querySelectorAll(".category-checkbox:checked"))
            .map(checkbox => checkbox.value.trim().toLowerCase());

        console.log("Selected Categories:", selectedCategories);

        if (selectedCategories.length === 0) {
            console.log("No category selected! Showing all modules and clearing arranged section.");
            resetModuleDisplay();
            return;
        }

        availableModules.querySelectorAll("li").forEach(function (li) {
            var moduleCategories = li.dataset.categories
                ? li.dataset.categories.split(",").map(cat => cat.trim().toLowerCase())
                : [];

            if (selectedCategories.some(cat => moduleCategories.includes(cat))) {
                li.style.display = "flex";
            } else {
                li.style.display = "none";
                var moduleId = li.querySelector("input").value;
                removeModuleById(moduleId);
                availableModules.querySelector(`input[value="${moduleId}"]`).checked = false;
            }
        });

        var toRemove = [];
        sortableModules.querySelectorAll("li").forEach(function (arrangedLi) {
            var moduleId = arrangedLi.dataset.moduleId;
            var matchingModule = availableModules.querySelector(`input[value="${moduleId}"]`);

            if (!matchingModule || matchingModule.closest("li").style.display === "none") {
                toRemove.push(moduleId);
            }
        });

        toRemove.forEach(moduleId => removeModuleById(moduleId));

        updateModuleNumbers();
        updateModuleOrderInput();
    });

    function resetModuleDisplay() {
        availableModules.querySelectorAll("li").forEach(li => {
            li.style.display = "flex";
            li.querySelector("input").checked = false;
        });

        sortableModules.innerHTML = "";
        updateModuleNumbers();
        updateModuleOrderInput();
    }
});
