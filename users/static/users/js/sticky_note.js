document.addEventListener('DOMContentLoaded', function () {
    const stickyNote = document.querySelector('.sticky-note');
    const textarea = stickyNote.querySelector('textarea');
    const bulletBtn = stickyNote.querySelector('.bullet-btn');

    let isBulleted = false; // Track whether the text is bulleted

    // ✅ Fetch user's notes when page loads
    fetch('users/get-notes/')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.content) {
                textarea.value = data.content; // Populate textarea with saved notes
                console.log("Fetched sticky note:", data.content);
            }
        })
        .catch(error => {
            console.error('Error fetching notes:', error);
        });

    // ✅ Save notes to backend whenever text changes
    textarea.addEventListener('input', () => {
        saveNotesToBackend(textarea.value);
    });

    // ✅ Save notes when losing focus
    textarea.addEventListener('blur', () => {
        saveNotesToBackend(textarea.value);
    });

    // ✅ Toggle bulleted list
    bulletBtn.addEventListener('click', () => {
        isBulleted = !isBulleted;
        updateTextarea();
    });

    function updateTextarea() {
        const lines = textarea.value.split('\n');

        if (isBulleted) {
            textarea.value = lines.map(line => line.startsWith('•') ? line : `• ${line}`).join('\n');
        } else {
            textarea.value = lines.map(line => line.replace(/^•\s*/, '')).join('\n');
        }

        saveNotesToBackend(textarea.value);
    }

    // ✅ Save notes to backend
    function saveNotesToBackend(content) {
        fetch('/save-notes/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ content: content }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Sticky note saved:', content);
            } else {
                console.error('Error saving note:', data.error);
            }
        })
        .catch(error => {
            console.error('Error saving notes:', error);
        });
    }

    // ✅ Get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
