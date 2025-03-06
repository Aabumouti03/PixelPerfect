// Function to format date as YYYY-MM-DD
function getFormattedDate(date) {
    const d = new Date(date);
    return d.toISOString().split("T")[0];  // Extracts YYYY-MM-DD format
}

// Function to fetch journal data for a specific date
function fetchJournalEntry(date) {
    fetch(`/journal/${date}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.data) {
                document.getElementById("sleep_hours").value = data.data.sleep_hours || "";
                document.getElementById("hydration").value = data.data.hydration || "";
                document.getElementById("stress").value = data.data.stress || "";

                if (data.data.coffee === "yes") {
                    document.getElementById("coffee_yes").checked = true;
                } else if (data.data.coffee === "no") {
                    document.getElementById("coffee_no").checked = true;
                }

                document.getElementById("notes").value = data.data.notes || "";
            } else {
                // Clear inputs if no previous entry exists
                document.getElementById("sleep_hours").value = "";
                document.getElementById("hydration").value = "";
                document.getElementById("stress").value = "low";  // Default to "low"
                document.getElementById("coffee_yes").checked = false;
                document.getElementById("coffee_no").checked = false;
                document.getElementById("notes").value = "";
            }
        })
        .catch(error => console.error("Error fetching journal entry:", error));
}


// Function to save journal entry via AJAX
function saveJournalEntry(event) {
    event.preventDefault();  // Prevent default form submission

    const journalForm = document.getElementById("journal-form");
    const successMessage = document.getElementById("success-message");
    const journalDate = document.getElementById("journal-date").value;

    const formData = {
        date: journalDate,
        sleep_hours: document.getElementById("sleep_hours").value,
        coffee: document.querySelector('input[name="coffee"]:checked') ? document.querySelector('input[name="coffee"]:checked').value : null,
        hydration: document.getElementById("hydration").value,
        stress: document.getElementById("stress").value,
        notes: document.getElementById("notes").value,
    };

    fetch("/journal/submit/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            successMessage.classList.remove("hidden");
            successMessage.textContent = "✅ Your entry has been saved!";
            setTimeout(() => successMessage.classList.add("hidden"), 3000);  // Hide message after 3 seconds
        } else {
            alert("Error saving entry: " + data.error);
        }
    })
    .catch(error => console.error("Error saving journal entry:", error));
}



document.addEventListener("DOMContentLoaded", function() {
    const journalForm = document.getElementById("journal-form");
    const successMessage = document.getElementById("success-message");

    journalForm.addEventListener("submit", function(event) {
        event.preventDefault(); // Stop default form submission

        const formData = {
            date: document.getElementById("journal-date").value, // Ensure it's formatted properly
            sleep_hours: document.getElementById("sleep_hours").value || null,
            coffee: document.querySelector("input[name='coffee']:checked") ? document.querySelector("input[name='coffee']:checked").value : null,
            hydration: document.getElementById("hydration").value || null,
            stress: document.getElementById("stress").value || null,
            notes: document.getElementById("notes").value.trim() || null
        };

        console.log("📤 [DEBUG] Sending Data to Server:", formData);

        fetch("/journal/submit/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())  // Expect JSON response
        .then(data => {
            console.log("🔄 [DEBUG] Server Response:", data);
            if (data.success) {
                successMessage.classList.remove("hidden");
                successMessage.innerText = "✅ Your entry has been saved!";
                setTimeout(() => {
                    successMessage.classList.add("hidden");
                }, 3000);
            } else {
                console.error("❌ [ERROR] Failed to save entry:", data.error);
            }
        })
        .catch(error => {
            console.error("⚠️ [NETWORK ERROR]:", error);
        });
    });
});
