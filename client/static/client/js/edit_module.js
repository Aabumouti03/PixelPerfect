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

function addResource(moduleId) {
    const dropdown = document.getElementById('resource-dropdown');
    const resourceId = dropdown.value;

    if (!resourceId) return alert("Select a resource");

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
            const option = dropdown.querySelector(`option[value="${resourceId}"]`);
            const title = option.textContent;

            // Remove the 'no resources' message if it exists
            const noResourcesMsg = document.getElementById('no-resources-msg');
            if (noResourcesMsg) noResourcesMsg.remove();

            // Create new resource item
            const list = document.getElementById('selected-resources');
            const li = document.createElement('li');
            li.id = `resource-${resourceId}`;
            li.innerHTML = `
            <input type="checkbox" name="remove_resource" value="${resourceId}" class="form-check-input me-2">
            ${title}
            `;

            list.appendChild(li);

            // Disable the option and reset dropdown
            option.disabled = true;
            dropdown.value = '';
        } else {
            alert(data.error || "Failed to add resource.");
        }
    })
    .catch(err => {
        console.error(err);
        alert("Something went wrong.");
    });
}

function removeSelectedResources(moduleId) {
    const selectedResources = Array.from(document.querySelectorAll('input[name="remove_resource"]:checked'))
        .map(el => el.value);

    if (selectedResources.length === 0) {
        alert("Select at least one resource to remove.");
        return;
    }


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
        console.log("Response from server:", data);

        if (data.success) {
            selectedResources.forEach(resourceId => {
                const resourceElement = document.getElementById(`resource-${resourceId}`);
                if (resourceElement) resourceElement.remove();
            });
        
            const remaining = document.querySelectorAll('#selected-resources li');
            if (remaining.length === 0) {
                const list = document.getElementById('selected-resources');
                const li = document.createElement('li');
                li.id = 'no-resources-msg';
                li.textContent = 'No resources linked yet.';
                list.appendChild(li);
            }
        
            alert("Selected resources removed.");
        }
         else {
            alert(data.error || "Failed to remove selected resources.");
        }
    })
    .catch(err => {
        console.error("Fetch error:", err);
        alert("Something went wrong.");
    });
}

function addVideo(moduleId) {
    const videoDropdown = document.getElementById('video-dropdown');
    const videoId = videoDropdown.value;

    if (!videoId) return alert("Select a video");


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
            const selectedOption = videoDropdown.querySelector(`option[value="${videoId}"]`);
            const videoTitle = selectedOption.textContent;

            // Remove "no videos" message if it exists
            const noVideosMsg = document.getElementById('no-videos-msg');
            if (noVideosMsg) noVideosMsg.remove();

            // Add video to the DOM
            const videoList = document.getElementById('selected-videos');
            const li = document.createElement('li');
            li.id = `video-${videoId}`;
            li.innerHTML = `
                <input type="checkbox" name="remove_video" value="${videoId}" class="form-check-input me-2">
                ${videoTitle}
            `;
            videoList.appendChild(li);

            selectedOption.disabled = true;
            videoDropdown.value = '';
        } else {
            alert(data.error || "Failed to add video.");
        }
    })
    .catch(err => {
        console.error(err);
        alert("Something went wrong.");
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

            const remaining = document.querySelectorAll('#selected-videos li');
            if (remaining.length === 0) {
                const videoList = document.getElementById('selected-videos');
                const li = document.createElement('li');
                li.id = 'no-videos-msg';
                li.textContent = 'No videos linked yet.';
                videoList.appendChild(li);
            }

            alert("Selected videos removed.");
        } else {
            alert("Failed to remove selected videos.");
        }
    })
    .catch(err => {
        console.error("Fetch error:", err);
        alert("Something went wrong.");
    });
}


function saveModuleChanges(moduleId) {

    const selectedVideos = Array.from(document.querySelectorAll('#selected-videos input[type="checkbox"]'))
        .map(el => el.value);

    const selectedResources = Array.from(document.querySelectorAll('#selected-resources input[type="checkbox"]'))
        .map(el => el.value);

    fetch(`/save_module_changes/${moduleId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            videos: selectedVideos.join(","),
            resources: selectedResources.join(",")
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Module changes saved successfully!");
            location.reload();
        } else {
            alert(data.error || "Failed to save changes.");
        }
    })
    .catch(err => {
        console.error("Save module error:", err);
        alert("Something went wrong while saving changes.");
    });
}
