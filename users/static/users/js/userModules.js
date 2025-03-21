function searchModules(event) {
    const query = event.target.value.toLowerCase();
    const modules = document.querySelectorAll('.module-card');
    let count = 0;

    modules.forEach(module => {
        const title = module.querySelector('h3')?.innerText.toLowerCase();
        if (title.includes(query)) {
            module.style.display = 'flex';
            count++;
        } else {
            module.style.display = 'none';
        }
    });
}