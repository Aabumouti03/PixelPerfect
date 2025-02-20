document.addEventListener('DOMContentLoaded', function () {
    const stickyNote = document.querySelector('.sticky-note');
    const textarea = stickyNote.querySelector('textarea');
    const bulletBtn = stickyNote.querySelector('.bullet-btn');

    let isBulleted = false; // Track whether the text is bulleted

    // Fetch the user's notes from the backend when the page loads
    fetch('/get-notes/')
        .then(response => response.json())
        .then(data => {
            if (data.content) {
                textarea.value = data.content; // Populate the textarea with saved notes
            }
        })
        .catch(error => {
            console.error('Error fetching notes:', error);
        });

    // Save notes to the backend whenever the text changes
    textarea.addEventListener('input', () => {
        saveNotesToBackend(textarea.value); // Save the text to the backend
        if (isBulleted) {
            const cursorPosition = textarea.selectionStart; // Save cursor position
            const lines = textarea.value.split('\n');

            // Add bullets to new lines
            const updatedText = lines.map((line, index) => {
                const trimmedLine = line.trim();
                return trimmedLine && !trimmedLine.startsWith('•') ? `• ${trimmedLine}` : line;
            }).join('\n');

            // Update the textarea value
            if (textarea.value !== updatedText) {
                textarea.value = updatedText;
                // Restore cursor position
                textarea.setSelectionRange(cursorPosition + 2, cursorPosition + 2); // Adjust cursor position for added bullets
            }
        }
    });

    // Toggle bulleted list
    bulletBtn.addEventListener('click', () => {
        isBulleted = !isBulleted; // Toggle the state
        updateTextarea();
    });

    // Convert text to bulleted list or plain text
    function updateTextarea() {
        const lines = textarea.value.split('\n'); // Split text into lines

        if (isBulleted) {
            // Add bullets to each non-empty line
            const bulletedText = lines.map(line => {
                const trimmedLine = line.trim();
                return trimmedLine && !trimmedLine.startsWith('•') ? `• ${trimmedLine}` : trimmedLine;
            }).join('\n');
            textarea.value = bulletedText;
        } else {
            // Remove bullets from each line
            const plainText = lines.map(line => line.replace(/^•\s*/, '')).join('\n');
            textarea.value = plainText;
        }

        // Save the updated text to the backend
        saveNotesToBackend(textarea.value);
    }

    // Function to save notes to the backend
    function saveNotesToBackend(content) {
        fetch('/save-notes/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),  // Include CSRF token for Django
            },
            body: JSON.stringify({ content: content }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Notes saved successfully:', data);
        })
        .catch(error => {
            console.error('Error saving notes:', error);
        });
    }

    // Helper function to get CSRF token
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