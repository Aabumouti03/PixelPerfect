document.addEventListener('DOMContentLoaded', function () {
    const stickyNote = document.querySelector('.sticky-note');
    const textarea = stickyNote.querySelector('textarea');
    const bulletBtn = stickyNote.querySelector('.bullet-btn');

    let isBulleted = false;

    fetch('/get-notes/')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.content) {
                textarea.value = data.content;
                console.log("Fetched sticky note:", data.content);
            }
        })
        .catch(error => {
            console.error('Error fetching notes:', error);
        });

        textarea.addEventListener('input', (event) => {
            saveNotesToBackend(textarea.value);
    
            if (isBulleted && event.inputType === 'insertLineBreak') {
                const position = textarea.selectionStart;
                const textBefore = textarea.value.substring(0, position);
                const textAfter = textarea.value.substring(position);
    
                textarea.value = textBefore + "• " + textAfter;
    
                textarea.selectionStart = textarea.selectionEnd = position + 2;
            }
        });

    textarea.addEventListener('blur', () => {
        saveNotesToBackend(textarea.value);
    });

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

    function saveNotesToBackend(content) {
        fetch('/save-notes/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken() 
            },
            body: JSON.stringify({ content: textarea.value }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('✅ Sticky note saved successfully:', textarea.value);
            } else {
                console.error('❌ Error saving note:', data.error);
            }
        })
        .catch(error => {
            console.error('❌ Network or server error:', error);
        });
        
    }
    
    function getCSRFToken() {
        return document.getElementById("csrf-token").value;
    }
});
