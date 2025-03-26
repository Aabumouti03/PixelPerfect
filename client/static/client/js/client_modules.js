function searchModules(event) {
    const query = event.target.value.toLowerCase();
    document.querySelectorAll('.module-card').forEach(module => {
      const titleElem = module.querySelector('h5');
      if (!titleElem) return; // If there's no <h5>, skip
  
      const title = titleElem.innerText.toLowerCase();
      // Show if it includes the query, hide if not
      module.style.display = title.includes(query) ? '' : 'none';
    });
  }