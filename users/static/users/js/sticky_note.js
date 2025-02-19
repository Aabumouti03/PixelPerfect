document.addEventListener('DOMContentLoaded', function () {
    const stickyNote = document.querySelector('.sticky-note');
    const textarea = stickyNote.querySelector('textarea');
    const bulletBtn = stickyNote.querySelector('.bullet-btn');

    let isBulleted = false; // Track whether the text is bulleted

    // Load saved notes from local storage
    const savedNotes = localStorage.getItem('stickyNoteContent');
    if (savedNotes) {
        textarea.value = savedNotes; // Populate the textarea with saved notes
    }

    // Save notes to local storage whenever the text changes
    textarea.addEventListener('input', () => {
        localStorage.setItem('stickyNoteContent', textarea.value); // Save the text
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

        // Save the updated text to local storage
        localStorage.setItem('stickyNoteContent', textarea.value);
    }
});