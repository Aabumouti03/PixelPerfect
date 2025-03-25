    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".enroll-button").forEach(button => {
            button.addEventListener("click", function () {
                const moduleId = this.getAttribute("data-module-id");
                const isEnrolled = this.getAttribute("data-enrolled") === "true";
                const action = isEnrolled ? "unenroll" : "enroll";

                // Toggle the UI immediately
                if (isEnrolled) {
                    this.textContent = "Enroll";
                    this.setAttribute("data-enrolled", "false");
                    this.classList.remove("enrolled");
                } else {
                    this.textContent = "Enrolled";
                    this.setAttribute("data-enrolled", "true");
                    this.classList.add("enrolled");
                }

                // Send request to update enrollment status
                const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");
                const modulesUrl = document.querySelector('meta[name="modules-url"]').getAttribute("content");

                fetch(modulesUrl, {
                    method: "POST",
                    headers: {
                      "Content-Type": "application/json",
                      "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({
                      module_id: moduleId,
                      action: action
                    })
                  })
                .then(response => response.json())
                .then(data => {
                    if (data.status === "success") {
                        console.log("Enrollment updated successfully");
                    } else {
                        console.error("Error updating enrollment");
                    }
                })
                .catch(error => console.error("Error:", error));
            });
        });
    });
