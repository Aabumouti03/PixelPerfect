document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".toggle-password").forEach(toggle => {
            toggle.addEventListener("click", function () {
                let input = this.previousElementSibling;
                let icon = this.querySelector("i");

                if (input.type === "password") {
                    input.type = "text";
                    
                    icon.classList.remove("bi-eye-slash");
                    
                    icon.classList.add("bi-eye");

                } else {
                    
                    input.type = "password";
                    
                    icon.classList.remove("bi-eye");
                    
                    icon.classList.add("bi-eye-slash");
                }
            });
        });
});
