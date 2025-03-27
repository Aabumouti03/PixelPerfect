// all_modules.js
// -----------------------------------------------------------
// This file handles the following for the all_modules page:
// 1) Logging each module's initial icon on DOM load
// 2) Searching/filtering modules by title
// 3) Toggling enrollment/unenrollment via fetch POST requests
// 4) Retrieving the CSRF token for secure requests
// -----------------------------------------------------------

// Once the DOM is ready, let's log each module's initial icon
function searchModules(event) {
  const query = event.target.value.toLowerCase();
  const modules = document.querySelectorAll('.module-card');

  modules.forEach(module => {
    const title = module.querySelector('h3')?.innerText.toLowerCase() || '';
    module.style.display = title.includes(query) ? '' : 'none';
  });
}

/* TOGGLE ENROLL/UNENROLL LOGIC
   Triggered when the user clicks the button (Add/Remove text).
   Sends a POST request to enroll or unenroll the module. */
function toggleModule(button, moduleTitle) {
  moduleTitle = moduleTitle.trim();

  let actionText = button.querySelector("span");
  let isEnrolled = button.dataset.enrolled === "true";
  let url = isEnrolled ? "/unenroll-module/" : "/enroll-module/";

  fetch(url, {
    method: "POST",
    body: JSON.stringify({ title: moduleTitle }),
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken()
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Toggle the enrollment state
      button.dataset.enrolled = (!isEnrolled).toString();
      // Update the button text
      actionText.innerText = isEnrolled ? "Add" : "Remove";
    } else {
      alert("Failed: " + data.error);
    }
  })
  .catch(error => console.error("Error:", error));
}

/* CSRF TOKEN HELPER
   Retrieves the 'csrftoken' from cookies so we can make secure POST requests. */
function getCSRFToken() {
  let cookies = document.cookie.split(';');
  for (let i = 0; i < cookies.length; i++) {
    let cookie = cookies[i].trim();
    if (cookie.startsWith("csrftoken=")) {
      return cookie.split("=")[1];
    }
  }
  return "";
}