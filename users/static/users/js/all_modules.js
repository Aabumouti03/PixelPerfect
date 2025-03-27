// all_modules.js
// -----------------------------------------------------------
// This file handles the following for the all_modules page:
// 1) Logging each module's initial icon on DOM load
// 2) Searching/filtering modules by title
// 3) Toggling enrollment/unenrollment via fetch POST requests
// 4) Retrieving the CSRF token for secure requests
// -----------------------------------------------------------

// Once the DOM is ready, let's log each module's initial icon
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.module-card').forEach(card => {
      let icon = card.querySelector("ion-icon");
      let title = card.querySelector("h3") ? card.querySelector("h3").innerText : "No Title";
      console.log("Module:", title, "Initial Icon:", icon.getAttribute("name"));
    });
  });
  
  /* SEARCH MODULES BY TITLE
     Called whenever the user types in the search bar. 
     Filters .module-card elements by matching the <h3> text. */
     function searchModules(event) {
        console.log("searchModules triggered!");
        const query = event.target.value.toLowerCase();
        const modules = document.querySelectorAll('.module-card');
        let count = 0;
      
        modules.forEach(module => {
          const title = module.querySelector('h3')?.innerText.toLowerCase() || '';
          
          if (title.includes(query)) {
            module.style.display = '';
            count++;
          } else {
            module.style.display = 'none';
          }
        });
      
      }
  
  /* TOGGLE ENROLL/UNENROLL LOGIC
     Triggered when the user clicks the Ionicon button (add/remove outline).
     Sends a POST request to enroll or unenroll the module. */
     function toggleModule(button, moduleTitle) {
      moduleTitle = moduleTitle.trim();
    
      let icon = button.querySelector("i");
      let isEnrolled = icon.classList.contains("fa-minus");
      let url = isEnrolled ? "/unenroll-module/" : "/enroll-module/";
    
      console.log("Clicked module:", `"${moduleTitle}"`,
                  "Enrolled?", isEnrolled,
                  "API URL:", url);
    
      let requestData = JSON.stringify({ title: moduleTitle });
    
      fetch(url, {
        method: "POST",
        body: requestData,
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken()
        }
      })
      .then(response => response.json())
      .then(data => {
        console.log("Server response:", data);
        if (data.success) {
          // 🔁 Toggle Font Awesome classes instead of ion-icon names
          icon.classList.remove(isEnrolled ? "fa-minus" : "fa-plus");
          icon.classList.add(isEnrolled ? "fa-plus" : "fa-minus");
        } else {
          console.error("Action failed:", data.error);
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