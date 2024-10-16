const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});

// Validate signup form before submission
document.getElementById("signup-form").addEventListener("submit", async function(event) {
    const password = this.password.value;
    const confirmPassword = this.confirm_password.value;

    // Check if passwords match
    if (password !== confirmPassword) {
        event.preventDefault(); // Prevent form submission
        alert("Passwords do not match.");
        return; // Exit the function early
    }

    event.preventDefault(); // Prevent default form submission

    const formData = new FormData(this);
    const data = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password'),
        full_name: formData.get('full_name'),
        role: "user" // Assign a default role; adjust as necessary
    };

    // Log the data to see what is being sent
    console.log("Signup Data:", JSON.stringify(data));

    try {
        const response = await fetch("http://127.0.0.1:8000/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });

        // Handle response
        const result = await response.json();
        console.log("Response:", result);
        
        if (response.ok) {
            alert("Signup successful! You can now log in.");
            // Redirect to index.html instead of a different server
            window.location.href = "index.html"; // Adjust path as necessary
            this.reset(); // Reset the form
        } else {
            const errorDetail = result.detail || "Signup failed. Please try again.";
            alert(`Error: ${errorDetail}`);
        }
    } catch (error) {
        console.error('Error during signup:', error);
        alert("An error occurred during signup. Please try again.");
    }
});

