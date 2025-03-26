    document.addEventListener("DOMContentLoaded", function() {
        // Password Toggle Logic
        const toggles = document.querySelectorAll(".password-toggle");
        
        toggles.forEach(toggle => {
            toggle.addEventListener("click", function() {
                const inputField = document.getElementById(this.getAttribute("data-target"));
    
                if (inputField.type === "password") {
                    inputField.type = "text";
                    this.classList.remove("fa-eye");
                    this.classList.add("fa-eye-slash"); // Switch to hide icon
                } else {
                    inputField.type = "password";
                    this.classList.remove("fa-eye-slash");
                    this.classList.add("fa-eye"); // Switch back to show icon
                }
            });
        });

    const form = document.querySelector("form");
    const password = document.getElementById("new_password");
    const confirmPassword = document.getElementById("confirm_password");

    form.addEventListener("submit", function(event) {
        if (password.value !== confirmPassword.value) {
            confirmPassword.setCustomValidity("Passwords do not match!");  // ALL ERRORS
            event.preventDefault(); // Stops form submission
        } else {
            confirmPassword.setCustomValidity(""); // Clears error if valid
        }
    });
    
    const ageField = document.getElementById("id_age");

    ageField.addEventListener("input", function () {
        if (this.validity.rangeUnderflow || this.validity.rangeOverflow) {
            this.setCustomValidity("Age must be between 18 and 100.");
        } else {
            this.setCustomValidity(""); // Reset the default validation
        }
    });

    });
