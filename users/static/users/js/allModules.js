function searchModules(event) {
    const query = event.target.value.toLowerCase();
    const modules = document.querySelectorAll('.module-card');

    modules.forEach(module => {
        const title = module.querySelector('h5').innerText.toLowerCase();
        module.style.display = title.includes(query) ? '' : 'none';
    });
}