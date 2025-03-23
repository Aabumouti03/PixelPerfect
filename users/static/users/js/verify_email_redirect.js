document.addEventListener("DOMContentLoaded", function () {
    let timeLeft = 7;
    let countdownElement = document.getElementById("countdown");

    let countdown = setInterval(function () {
        timeLeft--;
        countdownElement.textContent = timeLeft;
        if (timeLeft <= 0) {
            clearInterval(countdown);
            window.location.href = redirectUrl;
        }
    }, 1000);
});