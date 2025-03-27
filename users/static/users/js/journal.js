// Function to safely get an element
function getElement(id) {
    const element = document.getElementById(id);
    if (!element) {
        console.error(`❌ ERROR: Element with id '${id}' not found!`);
    }
    return element;
}

function parseDateString(dateString) {
    if (!dateString || typeof dateString !== "string") {
        console.error("❌ Invalid date string:", dateString);
        return null;
    }

    const parts = dateString.split("-");
    if (parts.length !== 3) {
        console.error("❌ Incorrect date format:", dateString);
        return null;
    }

    const [year, month, day] = parts.map(Number);

    if (isNaN(year) || isNaN(month) || isNaN(day)) {
        console.error("❌ Invalid date values:", dateString);
        return null;
    }

    return new Date(year, month - 1, day);
}

// Function to format date as YYYY-MM-DD
function getFormattedDate(dateString) {
    if (!dateString) return null;
    
    const date = parseDateString(dateString);
    if (!date || isNaN(date)) {
        console.error("❌ Invalid Date:", dateString);
        return null;
    }
    
    return date.toISOString().split("T")[0];  // Convert to YYYY-MM-DD
}
function fetchJournalEntry(date) {
    if (!date) return;

    fetch(`/journal/${date}/`, { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("✅ Data retrieved:", data.data);

                const fields = data.data;

                if (fields.sleep_hours) document.getElementById("sleep_hours").value = fields.sleep_hours;
                if (fields.hydration) document.getElementById("hydration").value = fields.hydration;
                if (fields.goal_progress) document.getElementById("goal_progress").value = fields.goal_progress;
                if (fields.notes) document.getElementById("notes").value = fields.notes;
                if (fields.stress) document.getElementById("stress").value = fields.stress;

                const radios = [
                    "connected_with_family",
                    "expressed_gratitude",
                    "caffeine",
                    "outdoors",
                    "sunset"
                ];
                
                radios.forEach(name => {
                    const value = fields[name];
                    if (value) {
                        document.querySelector(`input[name="${name}"][value="${value}"]`).checked = true;
                    }
                });
            }
        })
        .catch(error => console.error("❌ Fetch error: ", error));
}


function saveJournalEntry(event) {
    event.preventDefault();  // Prevent default form submission

    // Attempt to get the date from the hidden input first
    let formattedDate = document.getElementById("selected-date")?.value;

    // Fallback to URL extraction if the above doesn't work
    if (!formattedDate) {
        let currentURL = window.location.pathname;
        let dateMatch = currentURL.match(/\/journal\/(\d{4}-\d{2}-\d{2})\/?/);
        formattedDate = dateMatch ? dateMatch[1] : null;
    }

    if (!formattedDate) {
        alert("❌ Error: Invalid date. Unable to save entry.");
        return;
    }

    const formData = {
        date: formattedDate,
        sleep_hours: document.getElementById("sleep_hours")?.value || null,
        caffeine: document.querySelector('input[name="caffeine"]:checked')?.value || null,
        hydration: document.getElementById("hydration")?.value || null,
        stress: document.getElementById("stress")?.value || null,
        goal_progress: document.getElementById("goal_progress")?.value || null,
        notes: document.getElementById("notes")?.value || null,
        connected_with_family: document.querySelector('input[name="connected_with_family"]:checked')?.value || null,
        expressed_gratitude: document.querySelector('input[name="expressed_gratitude"]:checked')?.value || null,
        outdoors: document.querySelector('input[name="outdoors"]:checked')?.value || null,
        sunset: document.querySelector('input[name="sunset"]:checked')?.value || null,
    };

    console.log("📤 Sending Data to Server:", formData);

    fetch("/save_journal_entry/", {  
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")?.value,
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        console.log("📥 Response from Server:", data);

        if (data.success) {
            alert("✅ Your entry has been saved!");
        } else {
            alert("❌ Error saving entry: " + data.error);
        }
    })
    .catch(error => console.error("❌ Network error:", error));
}


document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Journal.js loaded successfully");

    // Extract the date from the URL or the context variable if available
    let currentURL = window.location.pathname;
    let dateMatch = currentURL.match(/\/journal\/(\d{4}-\d{2}-\d{2})\/?/);
    let journalDate = dateMatch ? dateMatch[1] : document.getElementById("selected-date")?.value;

    if (!journalDate) {
        journalDate = new Date().toISOString().split("T")[0];  // Use today's date as a fallback
    }

    console.log("📅 Extracted Date:", journalDate);

    if (journalDate) {
        fetchJournalEntry(journalDate);
    } else {
        console.error("❌ No valid date found!");
    }

    const form = document.getElementById("journal-form");
    if (form) {
        form.addEventListener("submit", saveJournalEntry);
    } else {
        console.error("❌ Journal form not found.");
    }
});
