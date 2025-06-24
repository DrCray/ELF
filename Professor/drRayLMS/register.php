<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username']);
    $password = password_hash(trim($_POST['password']), PASSWORD_DEFAULT);

    // Save user
    $line = "$username|$password\n";
    file_put_contents('data/users.txt', $line, FILE_APPEND);

    echo "Registration successful. <a href='index.php'>Login here</a>";
    exit;
}
?>

<h2>Register</h2>
<form method="post">
    Username: <input name="username" required><br>
    Password: <input type="password" name="password" required><br>
    <button type="submit">Register</button>
</form>

