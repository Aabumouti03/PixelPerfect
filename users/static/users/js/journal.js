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
    if (!date || typeof date !== "string" || date.trim() === "") {
        console.error("❌ Invalid date passed to fetchJournalEntry!");
        return;
    }

    console.log(`📥 Fetching journal entry for: ${date}`);

    fetch(`/journal/${date}/`, { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success && data.data) {
                console.log("✅ Data retrieved:", data.data);

                const fieldsToFill = [
                    { id: "sleep_hours", value: data.data.sleep_hours },
                    { id: "hydration", value: data.data.hydration },
                    { id: "stress", value: data.data.stress },
                    { id: "goal_progress", value: data.data.goal_progress || "low" },
                    { id: "notes", value: data.data.notes }
                ];

                // Populate text, number, and textarea fields
                fieldsToFill.forEach(field => {
                    const element = document.getElementById(field.id);
                    if (element) {
                        element.value = field.value || "";
                    }
                });

                // Handle radio buttons properly
                const radioFields = {
                    "connected_with_family": data.data.connected_with_family,
                    "expressed_gratitude": data.data.expressed_gratitude,
                    "caffeine": data.data.caffeine,
                    "spent_time_outdoors": data.data.outdoors,
                    "watched_sunset": data.data.sunset,
                };

                Object.keys(radioFields).forEach(fieldName => {
                    if (radioFields[fieldName] !== null && radioFields[fieldName] !== undefined) {
                        const radioButton = document.querySelector(`[name="${fieldName}"][value="${radioFields[fieldName]}"]`);
                        if (radioButton) {
                            radioButton.checked = true;
                        }
                    }
                });

            } else {
                console.warn("❌ No previous journal entry found for this date.");
                clearJournalForm();
            }
        })
        .catch(error => console.error("❌ Error fetching journal entry:", error));
}


function saveJournalEntry(event) {
    event.preventDefault();  // Prevent default form submission

    let currentURL = window.location.pathname;
    let dateMatch = currentURL.match(/\/journal\/(\d{4}-\d{2}-\d{2})\/?/);
    let formattedDate = dateMatch ? dateMatch[1] : null;

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
        spent_time_outdoors: document.querySelector('input[name="spent_time_outdoors"]:checked')?.value || null,
        watched_sunset: document.querySelector('input[name="watched_sunset"]:checked')?.value || null,
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
