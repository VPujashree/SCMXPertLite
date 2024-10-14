const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});

document.getElementById("signup-form").addEventListener("submit", function(event) {
    const password = this.password.value;
    const confirmPassword = this.confirm_password.value;
    if (password !== confirmPassword) {
        event.preventDefault(); // Prevent form submission
        alert("Passwords do not match.");
    }
});

document.getElementById("signup-form").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevent default form submission

    const formData = new FormData(this);
    const data = {};
    formData.forEach((value, key) => (data[key] = value));

    const response = await fetch("http://127.0.0.1:8000/signup", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });

    const result = await response.json();
    console.log(result);
    // Handle the result accordingly
});
