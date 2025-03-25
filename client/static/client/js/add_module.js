const selectedExerciseIds = new Set();
const selectedVideoIds = new Set();
const selectedResourceIds = new Set();

// Add selected exercise to preview and hidden inputs
function addExercise() {
    const dropdown = document.getElementById('exercise-dropdown');
    const exerciseId = dropdown.value;

    if (!exerciseId || selectedExerciseIds.has(exerciseId)) return;

    const selectedOption = dropdown.options[dropdown.selectedIndex];
    const title = selectedOption.getAttribute('data-title');
    const type = selectedOption.getAttribute('data-type');

    // Add preview item for exercise
    const li = document.createElement('li');
    li.className = 'list-group-item d-flex justify-content-between align-items-center';
    li.id = `exercise-preview-${exerciseId}`;
    li.innerHTML = `
        ${title} (${type})
        <button type="button" class="btn btn-danger btn-sm" onclick="removeExercise('${exerciseId}')">Remove</button>
    `;
    document.getElementById('selected-exercises').appendChild(li);

    // Add hidden input for exercise to form
    const hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.name = 'exercises';
    hidden.value = exerciseId;
    hidden.id = `hidden-exercise-${exerciseId}`;
    document.getElementById('hidden-exercise-inputs').appendChild(hidden);

    selectedExerciseIds.add(exerciseId);
}

// Remove selected exercise
function removeExercise(id) {
    selectedExerciseIds.delete(id);
    document.getElementById(`exercise-preview-${id}`)?.remove();
    document.getElementById(`hidden-exercise-${id}`)?.remove();
}

// Add selected video to preview and hidden inputs
function addVideo() {
    const dropdown = document.getElementById('video-dropdown');
    const videoId = dropdown.value;

    if (!videoId || selectedVideoIds.has(videoId)) return;

    const selectedOption = dropdown.options[dropdown.selectedIndex];
    const title = selectedOption.getAttribute('data-title');

    // Add preview item for video
    const li = document.createElement('li');
    li.className = 'list-group-item d-flex justify-content-between align-items-center';
    li.id = `video-preview-${videoId}`;
    li.innerHTML = `
        ${title}
        <button type="button" class="btn btn-danger btn-sm" onclick="removeVideo('${videoId}')">Remove</button>
    `;
    document.getElementById('selected-videos').appendChild(li);

    // Add hidden input for video to form
    const hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.name = 'videos';
    hidden.value = videoId;
    hidden.id = `hidden-video-${videoId}`;
    document.getElementById('hidden-video-inputs').appendChild(hidden);

    selectedVideoIds.add(videoId);
}

// Remove selected video
function removeVideo(id) {
    selectedVideoIds.delete(id);
    document.getElementById(`video-preview-${id}`)?.remove();
    document.getElementById(`hidden-video-${id}`)?.remove();
}

// Add selected resource to preview and hidden inputs
function addResource() {
    const dropdown = document.getElementById('resource-dropdown');
    const resourceId = dropdown.value;

    if (!resourceId || selectedResourceIds.has(resourceId)) return;

    const selectedOption = dropdown.options[dropdown.selectedIndex];
    const title = selectedOption.getAttribute('data-title');
    const type = selectedOption.getAttribute('data-type');
    const url = selectedOption.getAttribute('data-url');
    const file = selectedOption.getAttribute('data-file');

    // Add preview item for resource
    const li = document.createElement('li');
    li.className = 'list-group-item d-flex justify-content-between align-items-center';
    li.id = `resource-preview-${resourceId}`;
    li.innerHTML = `
        ${title} (${type})
        ${url ? `<a href="${url}" target="_blank" class="btn btn-info btn-sm">Open Link</a>` : ''}
        ${file ? `<a href="${file}" target="_blank" class="btn btn-info btn-sm">Download File</a>` : ''}
        <button type="button" class="btn btn-danger btn-sm" onclick="removeResource('${resourceId}')">Remove</button>
    `;
    document.getElementById('selected-resources').appendChild(li);

    // Add hidden input for resource to form
    const hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.name = 'resources';
    hidden.value = resourceId;
    hidden.id = `hidden-resource-${resourceId}`;
    document.getElementById('hidden-resource-inputs').appendChild(hidden);

    selectedResourceIds.add(resourceId);
}

// Remove selected resource
function removeResource(id) {
    selectedResourceIds.delete(id);
    document.getElementById(`resource-preview-${id}`)?.remove();
    document.getElementById(`hidden-resource-${id}`)?.remove();
}

function deleteResource(resourceId) {
    // Send AJAX request to delete the resource
    fetch(`/delete_resource/${resourceId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'), // CSRF token for POST requests
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Remove the deleted resource from the resources dropdown
            const resourceDropdown = document.getElementById('resource-dropdown');
            const optionToRemove = document.querySelector(`#resource-dropdown option[value="${data.resource_id}"]`);
            if (optionToRemove) {
                optionToRemove.remove();
            }
        }
    })
    .catch(error => console.error('Error deleting resource:', error));
}

// Example of handling delete resource button click
document.querySelectorAll('.delete-resource-btn').forEach(button => {
    button.addEventListener('click', function(event) {
        const resourceId = event.target.dataset.resourceId;
        deleteResource(resourceId);  // Call the function to delete the resource
    });
});

function deleteVideo(videoId) {
    // Send AJAX request to delete the video
    fetch(`/delete_video/${videoId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'), // CSRF token for POST requests
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Remove the deleted video from the video dropdown
            const videoDropdown = document.getElementById('video-dropdown');
            const optionToRemove = document.querySelector(`#video-dropdown option[value="${data.video_id}"]`);
            if (optionToRemove) {
                optionToRemove.remove();
            }
        }
    })
    .catch(error => console.error('Error deleting video:', error));
}

// Example of handling delete video button click
document.querySelectorAll('.delete-video-btn').forEach(button => {
    button.addEventListener('click', function(event) {
        const videoId = event.target.dataset.videoId;
        deleteVideo(videoId);  // Call the function to delete the video
    });
});