<?php
/**
 * Vulnerable Login Page — used for SQL Injection attack
 * Connects to MySQL, uses string concatenation (no prepared statements)
 * Vulnerable to: SQL Injection (T1190), Brute Force (T1110.001)
 *
 * Setup:
 *   sudo mysql
 *   CREATE DATABASE webapp;
 *   USE webapp;
 *   CREATE TABLE users (
 *       id INT AUTO_INCREMENT PRIMARY KEY,
 *       username VARCHAR(50),
 *       password VARCHAR(50),
 *       email VARCHAR(100),
 *       role VARCHAR(20) DEFAULT 'user'
 *   );
 *   INSERT INTO users (username, password, email, role) VALUES
 *   ('admin', '123123', 'admin@company.com', 'admin'),
 *   ('yaseen', 'letmein', 'yaseen@company.com', 'user'),
 *   ('john', 'password', 'john@company.com', 'user');
 */
session_start();

$db = mysqli_connect("localhost", "root", "", "webapp");

$error = "";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // VULNERABLE: user input injected directly into SQL string
    $query  = "SELECT * FROM users WHERE username='$username' AND password='$password'";
    $result = mysqli_query($db, $query);

    if ($result && mysqli_num_rows($result) > 0) {
        $user = mysqli_fetch_assoc($result);
        $_SESSION['logged_in'] = true;
        $_SESSION['username']  = $user['username'];
        $_SESSION['role']      = $user['role'];
        header('Location: /dashboard.php');
        exit;
    } else {
        $error = "Login failed. " . mysqli_error($db);
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
