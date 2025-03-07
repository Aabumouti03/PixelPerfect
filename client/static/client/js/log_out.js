document.addEventListener("DOMContentLoaded", function () {
    let logoutLink = document.getElementById("logout-link");
    let logoutModal = document.getElementById("logout-modal");
    let cancelLogout = document.getElementById("cancel-logout");

    if (logoutLink && logoutModal && cancelLogout) {

        logoutLink.addEventListener("click", function (event) {
            event.preventDefault();
            logoutModal.style.display = "flex";
        });


        cancelLogout.addEventListener("click", function () {
            logoutModal.style.display = "none";
        });
    }
});
