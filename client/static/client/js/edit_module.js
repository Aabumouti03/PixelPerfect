function enableEdit(fieldId) {
    const field = document.getElementById(fieldId);
    const fieldType = fieldId.split('-')[1];
    const saveBtn = document.getElementById(`save-${fieldType}`);
    field.removeAttribute("readonly");
    field.classList.add("border", "border-warning");
    saveBtn.classList.remove("d-none");
}

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



function addVideo(moduleId) {
    const videoDropdown = document.getElementById('video-dropdown');
    const videoId = videoDropdown.value;

    if (!videoId) return alert("Select a video");

    // Add video ID to hidden input
    const hiddenVideosInput = document.getElementById('hidden-videos');
    if (!hiddenVideosInput.value.includes(videoId)) {
        hiddenVideosInput.value += videoId + ",";
    }

    // Proceed with AJAX request
    fetch(`/add_video_to_module/${moduleId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ video_id: videoId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // On success, update the UI
            const selectedOption = videoDropdown.querySelector(`option[value="${videoId}"]`);
            const videoTitle = selectedOption.textContent;

            // Add video to the list dynamically
            const videoList = document.getElementById('selected-videos');
            const li = document.createElement('li');
            li.id = `video-${videoId}`;
            li.innerHTML = `${videoTitle} <button type="button" class="btn btn-secondary btn-sm" onclick="removeVideo('${moduleId}', '${videoId}')">Remove</button>`;
            videoList.appendChild(li);

            // Disable the option in the dropdown and reset
            selectedOption.disabled = true;
            videoDropdown.value = ''; // Reset dropdown
        } else {
            alert(data.error || "Failed to add video.");
        }
    })
    .catch(err => {
        alert("Something went wrong.");
        console.error(err);
    });
}




function addResource(moduleId) {
    const resourceDropdown = document.getElementById('resource-dropdown');
    const resourceId = resourceDropdown.value;

    if (!resourceId) return alert("Select a resource");

    // Add resource ID to hidden input
    const hiddenResourcesInput = document.getElementById('hidden-resources');
    if (!hiddenResourcesInput.value.includes(resourceId)) {
        hiddenResourcesInput.value += resourceId + ",";
    }

    // Proceed with AJAX request
    fetch(`/add_resource_to_module/${moduleId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ resource_id: resourceId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const selectedOption = resourceDropdown.querySelector(`option[value="${resourceId}"]`);
            const resourceTitle = selectedOption.textContent;

            // Add resource to the list dynamically
            const resourceList = document.getElementById('selected-resources');
            const li = document.createElement('li');
            li.id = `resource-${resourceId}`;
            li.innerHTML = `${resourceTitle} <button type="button" class="btn btn-secondary btn-sm" onclick="removeResource('${moduleId}', '${resourceId}')">Remove</button>`;
            resourceList.appendChild(li);

            // Disable the option in the dropdown and reset
            selectedOption.disabled = true;
            resourceDropdown.value = ''; // Reset dropdown
        } else {
            alert(data.error || "Failed to add resource.");
        }
    })
    .catch(err => {
        alert("Something went wrong.");
        console.error(err);
    });
}



// Function to remove resource from the module
function removeResource(moduleId, resourceId) {
    const resourceElement = document.getElementById(`resource-${resourceId}`);
    if (resourceElement) {
        resourceElement.remove();
    }

    // Send AJAX request to remove resource from the database
    $.ajax({
        url: '/remove_resource/',  // Adjust URL accordingly
        type: 'POST',
        data: {
            'module_id': moduleId,
            'resource_id': resourceId,
            'csrfmiddlewaretoken': csrfToken
        },
        success: function(response) {
            console.log('Resource removed successfully');
        },
        error: function(error) {
            console.error('Error:', error);
        }
    });
}

function removeSelectedVideos(moduleId) {
    const selectedVideos = Array.from(document.querySelectorAll('input[name="remove_video"]:checked'))
        .map(el => el.value);
    if (selectedVideos.length === 0) return alert("Select at least one video to remove.");

    fetch(`/remove_video_from_module/${moduleId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ video_ids: selectedVideos })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            selectedVideos.forEach(videoId => {
                const videoElement = document.getElementById(`video-${videoId}`);
                if (videoElement) videoElement.remove();
            });
            alert("Selected videos removed.");
        } else {
            alert("Failed to remove selected videos.");
        }
    });
}

function removeSelectedResources(moduleId) {
    const selectedResources = Array.from(document.querySelectorAll('input[name="remove_resource"]:checked'))
        .map(el => el.value);
    if (selectedResources.length === 0) return alert("Select at least one resource to remove.");

    fetch(`/remove_resource_from_module/${moduleId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ resource_ids: selectedResources })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            selectedResources.forEach(resourceId => {
                const resourceElement = document.getElementById(`resource-${resourceId}`);
                if (resourceElement) resourceElement.remove();
            });
            alert("Selected resources removed.");
        } else {
            alert("Failed to remove selected resources.");
        }
    });
}
