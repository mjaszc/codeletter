function dropdownMenuToggle() {
    const dropdown = document.getElementById("dropdown");
    if (dropdown.classList.contains('hidden')) {
        dropdown.classList.remove('hidden');
    } else {
        dropdown.classList.add('hidden');
    }
}