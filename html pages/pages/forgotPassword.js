function toggleOriginalPasswordVisibility() {
    const passwordInput = document.getElementById('original-password');
    const toggleIcon = passwordInput.nextElementSibling;
    passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
    toggleIcon.classList.toggle('fa-eye');
    toggleIcon.classList.toggle('fa-eye-slash');
}

function toggleNewPasswordVisibility() {
    const passwordInput = document.getElementById('new-password');
    const toggleIcon = passwordInput.nextElementSibling;
    passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
    toggleIcon.classList.toggle('fa-eye');
    toggleIcon.classList.toggle('fa-eye-slash');
}

function toggleConfirmNewPasswordVisibility() {
    const passwordInput = document.getElementById('confirm-new-password');
    const toggleIcon = passwordInput.nextElementSibling;
    passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
    toggleIcon.classList.toggle('fa-eye');
    toggleIcon.classList.toggle('fa-eye-slash');
}

function resetPassword() {
    // Implement your password reset logic here
    alert('Password reset functionality not implemented.');
}
