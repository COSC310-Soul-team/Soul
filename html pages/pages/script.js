function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.querySelector('.eyesicon_c');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

function toggleRepasswordVisibility() {
    const repasswordInput = document.getElementById('repassword');
    const toggleIcon = document.querySelector('.eyesicon_c1');
    if (repasswordInput.type === 'password') {
        repasswordInput.type = 'text';
        toggleIcon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        repasswordInput.type = 'password';
        toggleIcon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

function validateForm() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const repassword = document.getElementById('repassword').value;
    const email = document.getElementById('email').value;
    const role = document.querySelector('input[name="role"]:checked').value;

    if (username === '' || password === '') {
        alert('Please enter both username and password');
        return;
    } else if (password !== repassword) {
        alert('Re-entered password does not match the password');
        return;
    }

    // Example fetch for registration (adjust URL and handle response accordingly)
    console.log({ username, password, email, role });
    // Add your fetch call here
    alert('Registration successful!'); // Placeholder success message
}
