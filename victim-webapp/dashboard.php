<?php
/**
 * Protected Dashboard — redirect target after successful login
 * Works with both login_basic.php and login_sqli.php
 */
session_start();

if (!isset($_SESSION['logged_in'])) {
    header('Location: /login.php');
    exit;
}
?>
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
  <h2>Welcome, <?= htmlspecialchars($_SESSION['username'] ?? 'User') ?>!</h2>
  <p>Role: <?= htmlspecialchars($_SESSION['role'] ?? 'unknown') ?></p>
  <p>You are logged in.</p>
  <br>
  <a href="/search.php">User Search</a>
</body>
</html>
