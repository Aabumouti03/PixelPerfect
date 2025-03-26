
document.addEventListener("DOMContentLoaded", function () {
    var collapsibles = document.querySelectorAll(".collapsible");

    collapsibles.forEach(function (collapsible) {
        collapsible.addEventListener("click", function () {
            this.classList.toggle("active");
            var content = this.nextElementSibling;

            // Ensure the content exists before manipulating it
            if (content && content.classList.contains("collapsible-content")) {
                if (content.style.display === "block") {
                    content.style.display = "none";
                } else {
                    content.style.display = "block";
                }
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
const stars = document.querySelectorAll(".star");
const ratingValue = document.getElementById("rating-value");
const csrfToken = "{{ csrf_token }}"; // Ensure CSRF token is included

const userRating = parseInt("{{ user_rating }}", 10);  // ✅ Fetch user's rating
const averageRating = parseFloat("{{ module.average_rating|default:0 }}"); // ✅ Fetch average rating

function updateStars(userRating) {
stars.forEach(star => {
    let starValue = parseInt(star.getAttribute("data-value"));
    if (starValue <= userRating) {
        star.classList.add("selected"); // ✅ Highlight user rating
    } else {
        star.classList.remove("selected");
    }
});
}

// ✅ Initialize stars based on user's rating
updateStars(isNaN(userRating) ? 0 : userRating);

// ✅ Display the average rating in the text
ratingValue.textContent = `(Rated: ${averageRating.toFixed(1)}/5)`;

stars.forEach(star => {
star.addEventListener("click", function () {
    const rating = parseInt(this.getAttribute("data-value"));

    fetch("{% url 'rate_module' module.id %}", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({ rating: rating })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateStars(rating);  // ✅ Update selected stars with the user's rating
            ratingValue.textContent = `(Rated: ${data.average_rating.toFixed(1)}/5)`;
        } else {
            alert("Error submitting rating.");
        }
    })
    .catch(error => console.error("Error:", error));
});
});
});


document.addEventListener("DOMContentLoaded", function () {
var progressChart;  // Store progress chart globally
var ctx = document.getElementById('progressChart').getContext('2d');

function updateProgressChart(progressValue) {
if (progressChart) {
    progressChart.data.datasets[0].data = [progressValue, 100 - progressValue];
    progressChart.update();
} else {
    progressChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [progressValue, 100 - progressValue],
                backgroundColor: ['#4A90E2', '#E0E0E0'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '75%',
            responsive: false,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
}
}

// Initialize progress chart with initial value
var initialProgress = parseFloat("{{ progress_value }}");
updateProgressChart(isNaN(initialProgress) ? 0 : initialProgress);

document.querySelectorAll(".done-button").forEach(button => {
button.addEventListener("click", function () {
    const itemId = this.getAttribute("data-id");
    const itemType = this.getAttribute("data-type");
    const currentText = this.textContent.trim();
    const action = currentText === "Done" ? "done" : "undo"; 

    // Toggle button text
    this.textContent = action === "done" ? "Undo" : "Done";

    fetch("{% url 'mark_done' %}", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": "{{ csrf_token }}"
        },
        body: JSON.stringify({ id: itemId, type: itemType, action: action })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update progress value and chart
            const updatedProgress = data.updated_progress || 0;
            document.getElementById("progress-value").textContent = `${updatedProgress}%`;
            updateProgressChart(updatedProgress);
        } else {
            alert("Error updating progress.");
        }
    })
    .catch(error => console.error("Error:", error));
});
});
});
