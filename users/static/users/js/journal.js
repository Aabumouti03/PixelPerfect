// Function to safely get an element
function getElement(id) {
    const element = document.getElementById(id);
    if (!element) {
        console.error(`❌ ERROR: Element with id '${id}' not found!`);
    }
    return element;
}

// Function to format date as YYYY-MM-DD
function getFormattedDate(dateString) {
    if (!dateString) return null;
    
    const date = new Date(dateString);
    if (isNaN(date)) {
        console.error("❌ Invalid Date:", dateString);
        return null;
    }
    
    return date.toISOString().split("T")[0];  // Convert to YYYY-MM-DD
}


// Function to fetch journal entry for a specific date
function fetchJournalEntry(date) {
    console.log(`📥 Fetching journal entry for ${date}`);

    fetch(`/journal/${date}/`)
        .then(response => response.json())
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
                document.querySelector(`[name="connected_with_family"][value="${data.data.connected_with_family}"]`)?.setAttribute("checked", true);
                document.querySelector(`[name="expressed_gratitude"][value="${data.data.expressed_gratitude}"]`)?.setAttribute("checked", true);
                document.querySelector(`[name="caffeine"][value="${data.data.caffeine}"]`)?.setAttribute("checked", true);
                document.querySelector(`[name="outdoors"][value="${data.data.outdoors}"]`)?.setAttribute("checked", true);
                document.querySelector(`[name="sunset"][value="${data.data.sunset}"]`)?.setAttribute("checked", true);
            } else {
                console.warn("❌ No previous journal entry found for this date.");

                // Clear the form fields if no entry is found
                getElement("sleep_hours").value = "";
                getElement("hydration").value = "";
                getElement("stress").value = "low";
                getElement("goal_progress").value = "low";
                getElement("notes").value = "";

                document.querySelectorAll('[name="connected_with_family"]').forEach(el => el.checked = false);
                document.querySelectorAll('[name="expressed_gratitude"]').forEach(el => el.checked = false);
                document.querySelectorAll('[name="caffeine"]').forEach(el => el.checked = false);
                document.querySelectorAll('[name="outdoors"]').forEach(el => el.checked = false);
                document.querySelectorAll('[name="sunset"]').forEach(el => el.checked = false);
            }
        })
        .catch(error => console.error("❌ Error fetching journal entry:", error));
}

// Function to save journal entry
function saveJournalEntry(event) {
    event.preventDefault();  // Prevent default form submission

    // Get the date value correctly
    let rawDate = document.getElementById("journal-date")?.value;
    let formattedDate = getFormattedDate(rawDate); // Ensure it's in YYYY-MM-DD format

    if (!formattedDate) {
        alert("❌ Error: Invalid date selected.");
        return;
    }

    const formData = {
        date: formattedDate,  // Ensure date is in YYYY-MM-DD format
        sleep_hours: document.getElementById("sleep_hours")?.value || null,
        caffeine: document.querySelector('input[name="caffeine"]:checked')?.value || null,
        hydration: document.getElementById("hydration")?.value || null,
        stress: document.getElementById("stress")?.value || null,
        goal_progress: document.getElementById("goal_progress")?.value || null,
        notes: document.getElementById("notes")?.value || null
    };

    console.log("📤 Sending Data to Server:", formData); // Debugging

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
        console.log("📥 Response from Server:", data); // Debugging

        if (data.success) {
            alert("✅ Your entry has been saved!");
        } else {
            alert("❌ Error saving entry: " + data.error);
        }
    })
    .catch(error => console.error("❌ Network error:", error));
}


// Attach event listeners after page load
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Journal.js loaded successfully");

    // Correcting getElement → document.getElementById()
    const form = document.getElementById("journal-form");
    if (form) {
        form.addEventListener("submit", saveJournalEntry);
    } else {
        console.error("❌ Journal form not found.");
    }

    // Ensure journal date input is correctly retrieved
    const journalDateInput = document.getElementById("journal-date");
    if (journalDateInput) {
        console.log("📅 Journal Date:", journalDateInput.value); // Debugging

        // Fetch journal entry for the current date
        fetchJournalEntry(journalDateInput.value);
    } else {
        console.error("❌ journal-date field not found!");
    }
});
