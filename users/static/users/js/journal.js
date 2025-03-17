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

// Function to fetch journal entry for a specific date
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

                // Populate form fields with saved data
                getElement("sleep_hours").value = data.data.sleep_hours || "";
                getElement("hydration").value = data.data.hydration || "";
                getElement("stress").value = data.data.stress || "";
                getElement("goal_progress").value = data.data.goal_progress || "low";
                getElement("notes").value = data.data.notes || "";

                // Ensure radio buttons are selected properly
                ["connected_with_family", "expressed_gratitude", "caffeine", "outdoors", "sunset"].forEach(field => {
                    if (data.data[field]) {
                        document.querySelector(`[name="${field}"][value="${data.data[field]}"]`)?.setAttribute("checked", true);
                    }
                });
            } else {
                console.warn("❌ No previous journal entry found for this date.");
                clearJournalForm();
            }
        })
        .catch(error => console.error("❌ Error fetching journal entry:", error));
}

// Function to save journal entry
function saveJournalEntry(event) {
    event.preventDefault();  // Prevent default form submission

    let rawDate = document.getElementById("journal-date")?.value;
    let formattedDate = getFormattedDate(rawDate); 

    if (!formattedDate) {
        alert("❌ Error: Invalid date selected.");
        return;
    }

    const formData = {
        date: formattedDate,
        sleep_hours: document.getElementById("sleep_hours")?.value || null,
        caffeine: document.querySelector('input[name="caffeine"]:checked')?.value || null,
        hydration: document.getElementById("hydration")?.value || null,
        stress: document.getElementById("stress")?.value || null,
        goal_progress: document.getElementById("goal_progress")?.value || null,
        notes: document.getElementById("notes")?.value || null
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

    // Extract the date from the URL and handle missing date cases
    let currentURL = window.location.pathname;
    let dateMatch = currentURL.match(/\/journal\/(\d{4}-\d{2}-\d{2})\/?/);

    let journalDate = dateMatch ? dateMatch[1] : new Date().toISOString().split("T")[0];

    console.log("📅 Extracted Date from URL:", journalDate);

    if (journalDate) {
        fetchJournalEntry(journalDate);  
    } else {
        console.error("❌ No valid date found in URL!");
    }

    const form = document.getElementById("journal-form");
    if (form) {
        form.addEventListener("submit", saveJournalEntry);
    } else {
        console.error("❌ Journal form not found.");
    }
});
