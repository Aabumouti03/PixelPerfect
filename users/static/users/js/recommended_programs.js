    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".enroll-button").forEach(button => {
            const isEnrolled = button.getAttribute("data-enrolled") === "true";
            if (isEnrolled) {
                button.textContent = "Enrolled";
                button.classList.add("enrolled");
            } else {
                button.textContent = "Enroll";
                button.classList.remove("enrolled");
            }

            button.addEventListener("click", function () {
                const programId = this.getAttribute("data-program-id");
                const isEnrolled = this.getAttribute("data-enrolled") === "true";
                const action = isEnrolled ? "unenroll" : "enroll";

                document.querySelectorAll(".enroll-button").forEach(b => {
                    if (b !== this && b.getAttribute("data-enrolled") === "true") {
                        b.textContent = "Enroll";
                        b.setAttribute("data-enrolled", "false");
                        b.classList.remove("enrolled");
                    }
                });

                if (isEnrolled) {
                    this.textContent = "Enroll";
                    this.setAttribute("data-enrolled", "false");
                    this.classList.remove("enrolled");
                } else {
                    this.textContent = "Enrolled";
                    this.setAttribute("data-enrolled", "true");
                    this.classList.add("enrolled");
                }

                const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");
                const programsUrl = document.querySelector('meta[name="programs-url"]').getAttribute("content");
                
                fetch(programsUrl, {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                  },
                  body: JSON.stringify({
                    program_id: programId,
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
