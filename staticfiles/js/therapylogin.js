 // Wrap the checkbox label to make the entire text clickable
 document.addEventListener('DOMContentLoaded', function() {
    const checkbox = document.querySelector('input[type="checkbox"]');
    if (checkbox) {
        const label = checkbox.nextSibling;
        const wrapper = document.createElement('label');
        wrapper.style.cursor = 'pointer';
        wrapper.appendChild(checkbox.cloneNode(true));
        wrapper.appendChild(label.cloneNode(true));
        checkbox.parentNode.replaceChild(wrapper, checkbox);
        label.remove();
}
});