new Sortable(document.getElementById('sortableModules'), {
    animation: 150,
    ghostClass: 'sortable-ghost',
});

function saveModuleOrder() {
    let orderData = [];
    document.querySelectorAll('#sortableModules .list-group-item').forEach((item, index) => {
        orderData.push({ id: item.dataset.id, order: index + 1 });
    });

    fetch("{% url 'update_module_order' program.id %}", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": "{{ csrf_token }}"
        },
        body: JSON.stringify({ order: orderData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Module order updated successfully!");
        } else {
            alert("Error updating order: " + data.error);
        }
    })
    .catch(error => {
        alert("Request failed: " + error);
    });
}
window.openModal = function(modalId) {
document.getElementById(modalId).style.display = 'flex';
document.body.style.overflow = 'hidden';

// Disable sortable interaction only on modal open
sortable.option('disabled', true);
};

window.closeModal = function(modalId) {
document.getElementById(modalId).style.display = 'none';
document.body.style.overflow = 'auto';

// Re-enable sortable interaction when modal is closed
sortable.option('disabled', false);
};
