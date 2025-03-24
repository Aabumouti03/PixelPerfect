// Enable the editing of the module title or description
function enableEdit(fieldId) {
    const field = document.getElementById(fieldId);
    const fieldType = fieldId.split('-')[1];
    const saveBtn = document.getElementById(`save-${fieldType}`);
    field.removeAttribute("readonly");
    field.classList.add("border", "border-warning");
    saveBtn.classList.remove("d-none");
}

// Save the edited title or description
function saveField(moduleId, fieldName) {
    const fieldId = fieldName === 'title' ? 'module-title' : 'module-description';
    const field = document.getElementById(fieldId);
    const saveBtn = document.getElementById(`save-${fieldName}`);
    const value = field.value;

    fetch(`/update_module/${moduleId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ field: fieldName, value: value })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            field.setAttribute("readonly", true);
            field.classList.remove("border", "border-warning");
            saveBtn.classList.add("d-none");
            alert("Module updated successfully!");
        } else {
            alert("Failed to update module.");
        }
    })
    .catch(err => {
        alert("Something went wrong.");
        console.error(err);
    });
}

// Add an exercise to the module
function addExercise(moduleId) {
    const exerciseId = document.getElementById('exercise-dropdown').value;
    if (!exerciseId) return alert("Select an exercise");

    fetch(`/add_exercise_to_module/${moduleId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ exercise_id: exerciseId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) location.reload();
        else alert("Failed to add exercise.");
    });
}

// Remove selected exercises from the module
function removeSelectedExercises(moduleId) {
    const selected = Array.from(document.querySelectorAll('input[name="remove_exercise"]:checked'))
        .map(el => el.value);
    if (selected.length === 0) return alert("Select at least one exercise to remove.");

    fetch(`/remove_exercises_from_module/${moduleId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ exercise_ids: selected })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) location.reload();
        else alert("Failed to remove exercise.");
    });
}

// Remove a video from the module
function removeVideo(moduleId, videoId) {
    fetch(`/remove_video_from_module/${moduleId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ video_id: videoId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) location.reload();
        else alert("Failed to remove video.");
    });
}

// Remove a resource from the module
function removeResource(moduleId, resourceId) {
    fetch(`/remove_resource_from_module/${moduleId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ resource_id: resourceId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) location.reload();
        else alert("Failed to remove resource.");
    });
}
