// Function to format date as YYYY-MM-DD
function getFormattedDate(date) {
    const d = new Date(date);
    return d.toISOString().split("T")[0];  // Extracts YYYY-MM-DD format
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
                document.getElementById("sleep_hours").value = data.data.sleep_hours || "";
                document.getElementById("hydration").value = data.data.hydration || "";
                document.getElementById("stress").value = data.data.stress || "";
                document.getElementById("goal_progress").value = data.data.goal_progress || "low";
                document.getElementById("notes").value = data.data.notes || "";

                document.querySelector(`[name="connected_with_family"][value="${data.data.connected_with_family}"]`)?.checked === true;
                document.querySelector(`[name="expressed_gratitude"][value="${data.data.expressed_gratitude}"]`)?.checked === true;
                document.querySelector(`[name="caffeine"][value="${data.data.caffeine}"]`)?.checked === true;
                document.querySelector(`[name="outdoors"][value="${data.data.outdoors}"]`)?.checked === true;
                document.querySelector(`[name="sunset"][value="${data.data.sunset}"]`)?.checked === true;
            } else {
                console.warn("❌ No previous journal entry found for this date.");

                // Clear the form fields if no entry is found
                document.getElementById("sleep_hours").value = "";
                document.getElementById("hydration").value = "";
                document.getElementById("stress").value = "low";
                document.getElementById("goal_progress").value = "low";
                document.getElementById("notes").value = "";

                document.querySelectorAll('[name="connected_with_family"]').forEach(el => el.checked = false);
                document.querySelectorAll('[name="expressed_gratitude"]').forEach(el => el.checked = false);
                document.querySelectorAll('[name="caffeine"]').forEach(el => el.checked = false);
                document.querySelectorAll('[name="outdoors"]').forEach(el => el.checked = false);
                document.querySelectorAll('[name="sunset"]').forEach(el => el.checked = false);
            }
        })
        .catch(error => console.error("❌ Error fetching journal entry:", error));
}
function saveJournalEntry(event) {
    event.preventDefault();  // Prevent default form submission

    const formData = {
        date: document.getElementById("journal-date").value,
        sleep_hours: document.getElementById("sleep_hours").value || null,
        caffeine: document.querySelector('input[name="caffeine"]:checked') ? document.querySelector('input[name="caffeine"]:checked').value : null,
        hydration: document.getElementById("hydration").value || null,
        stress: document.getElementById("stress").value || null,
        goal_progress: document.getElementById("goal_progress").value || null,
        notes: document.getElementById("notes").value || null
    };

    console.log("📤 Sending Data to Server:", formData); // Debugging

    fetch("/journal/save/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
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

// Attach event listener
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("journal-form").addEventListener("submit", saveJournalEntry);
});




// Ensure JavaScript runs when the page is loaded
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Journal.js loaded successfully");

    // Attach form submit event listener
    const form = document.getElementById("journal-form");
    if (form) {
        form.addEventListener("submit", saveJournalEntry);
    } else {
        console.error("❌ Journal form not found.");
    }

    // Fetch journal entry for the current date
    const currentDate = document.getElementById("journal-date").value;
    fetchJournalEntry(currentDate);
});
