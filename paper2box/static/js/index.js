let file_input = document.querySelector('#input-image');
let rocket_button = document.querySelector('#rocket-button');
rocket_button.style.display = "none";

file_input.onchange = function(event) {
    console.log(event);
    rocket_button.style.display = "flex";
}