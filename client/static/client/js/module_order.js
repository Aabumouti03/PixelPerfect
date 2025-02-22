document.addEventListener("DOMContentLoaded", function () {
    const availableModules = document.getElementById("availableModules");
    const sortableModules = document.getElementById("sortableModules");
    const moduleOrderInput = document.getElementById("module_order");

    // Function to update module order in the hidden input field
    function updateModuleOrder() {
        let order = [];
        document.querySelectorAll(".sortable-item").forEach(item => {
            let id = item.getAttribute("data-id");
            if (id) {
                order.push(id);
            }
        });
        moduleOrderInput.value = order.join(",");
    }

    // Initialize SortableJS for smooth drag and drop
    new Sortable(sortableModules, {
        animation: 150,
        ghostClass: "sortable-ghost",
        onEnd: function () {
            updateModuleOrder();
        }
    });

    // Move selected modules to the sortable list
    document.querySelectorAll(".module-checkbox").forEach(checkbox => {
        checkbox.addEventListener("change", function () {
            const moduleId = this.value;
            const moduleLabel = this.parentElement.textContent.trim();

            if (this.checked) {
                // Check if already added
                let existingItem = document.querySelector(`.sortable-item[data-id="${moduleId}"]`);
                if (!existingItem) {
                    // Create a draggable module item
                    let li = document.createElement("li");
                    li.className = "d-flex align-items-center sortable-item";
                    li.setAttribute("data-id", moduleId);
                    li.innerHTML = `
                        <span class="ms-2">${moduleLabel}</span>
                        <span class="ms-auto drag-handle">☰</span>
                    `;
                    sortableModules.appendChild(li);
                }
            } else {
                // Remove from sortable list if unchecked
                let selectedItem = document.querySelector(`.sortable-item[data-id="${moduleId}"]`);
                if (selectedItem) {
                    selectedItem.remove();
                }
            }
            updateModuleOrder();
        });
    });

    updateModuleOrder(); // Initial order update
});
