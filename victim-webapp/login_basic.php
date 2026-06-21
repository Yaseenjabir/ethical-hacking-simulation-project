<?php
/**
 * Basic Login Page — used for Web Brute Force attack
 * No database — credentials hardcoded
 * Vulnerable to: Brute Force (T1110.001)
 */
session_start();

$valid_user = 'admin';
$valid_pass = '123123';

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $user = $_POST['username'] ?? '';
    $pass = $_POST['password'] ?? '';

    if ($user === $valid_user && $pass === $valid_pass) {
        $_SESSION['logged_in'] = true;
        $_SESSION['username']  = $user;
        header('Location: /dashboard.php');
        exit;
    } else {
        $error = 'Invalid credentials';
    }
}
?>
<!DOCTYPE html>
<html>
<head><title>Admin Login</title></head>
<body>
  <h2>Admin Panel Login</h2>
  <?php if ($error): ?>
    <p style="color:red;"><?= $error ?></p>
  <?php endif; ?>
  <form method="POST">
    <input type="text"     name="username" placeholder="Username" /><br><br>
    <input type="password" name="password" placeholder="Password" /><br><br>
    <button type="submit">Login</button>
  </form>
</body>
</html>
