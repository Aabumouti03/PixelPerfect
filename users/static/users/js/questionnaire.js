document.addEventListener("DOMContentLoaded", () => {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    const questionnaireId = document.querySelector('meta[name="questionnaire-id"]').content;
    const questions = JSON.parse(document.getElementById("questions-data").textContent);

    let currentQuestionIndex = 0;
    let selectedAnswers = {};

    function updateQuestion() {
        const currentQuestion = questions[currentQuestionIndex];
        const questionText = document.getElementById("question-text");
        const answerOptions = document.getElementById("answer-options");
        const ratingOptions = document.getElementById("rating-options");

        questionText.innerText = currentQuestion.question_text;
        answerOptions.innerHTML = "";
        ratingOptions.innerHTML = "";
        answerOptions.style.display = "none";
        ratingOptions.style.display = "none";

        let selectedValue = selectedAnswers[currentQuestionIndex]?.value || null;

        if (currentQuestion.question_type === "AGREEMENT") {
            answerOptions.style.display = "block";
            answerOptions.innerHTML = `
                <button class="answer-btn" data-value="2">Strongly Agree</button>
                <button class="answer-btn" data-value="1">Agree</button>
                <button class="answer-btn" data-value="0">Neutral</button>
                <button class="answer-btn" data-value="-1">Disagree</button>
                <button class="answer-btn" data-value="-2">Strongly Disagree</button>
            `;
        } else if (currentQuestion.question_type === "RATING") {
            ratingOptions.style.display = "block";
            ratingOptions.innerHTML = `
                <button class="rating-btn" data-value="-2">1</button>
                <button class="rating-btn" data-value="-1">2</button>
                <button class="rating-btn" data-value="0">3</button>
                <button class="rating-btn" data-value="1">4</button>
                <button class="rating-btn" data-value="2">5</button>
            `;
        }

        if (selectedValue !== null) {
            document.querySelectorAll(".answer-btn, .rating-btn").forEach(btn => {
                if (parseInt(btn.dataset.value) === selectedValue) {
                    btn.classList.add("selected");
                }
            });
        }

        const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
        const progressBar = document.getElementById("progress-bar");
        progressBar.style.width = progress + "%";
        progressBar.innerText = Math.round(progress) + "%";

        document.getElementById("prev-btn").disabled = currentQuestionIndex === 0;
        document.getElementById("next-btn").disabled = !selectedAnswers[currentQuestionIndex];

        document.querySelectorAll(".answer-btn, .rating-btn").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const value = parseInt(e.target.dataset.value);
                selectedAnswers[currentQuestionIndex] = {
                    questionId: currentQuestion.id,
                    value: value,
                };

                document.querySelectorAll(".answer-btn, .rating-btn").forEach(b => b.classList.remove("selected"));
                e.target.classList.add("selected");

                document.getElementById("next-btn").disabled = false;
            });
        });
    }

    document.getElementById("next-btn").addEventListener("click", () => {
        if (currentQuestionIndex < questions.length - 1) {
            currentQuestionIndex++;
            updateQuestion();
        } else {
            submitResponses();
        }
    });

    document.getElementById("prev-btn").addEventListener("click", () => {
        if (currentQuestionIndex > 0) {
            currentQuestionIndex--;
            updateQuestion();
        }
    });

    function submitResponses() {
        const responseData = {
            questionnaireId: questionnaireId,
            responses: Object.values(selectedAnswers),
        };

        fetch("/submit-responses/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify(responseData)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                alert("Error: " + data.message);
            }
        })
        .catch(error => console.error("Error:", error));
    }

    // Logout Modal
    const logoutBtn = document.getElementById("logout-btn");
    const logoutModal = document.getElementById("logout-modal");
    const cancelLogout = document.getElementById("cancel-logout");

    logoutBtn.addEventListener("click", () => logoutModal.style.display = "block");
    cancelLogout.addEventListener("click", () => logoutModal.style.display = "none");

    window.onclick = function(event) {
        if (event.target === logoutModal) {
            logoutModal.style.display = "none";
        }
    };

    updateQuestion();
});
