<?php
/**
 * Vulnerable Search Page — used for UNION-based SQL Injection
 * Displays the raw SQL query so the attacker can see what is happening
 * Vulnerable to: SQL Injection (T1190) — UNION extraction, boolean blind
 */
$db = mysqli_connect("localhost", "webapp", "webapp123", "webapp");

$results     = [];
$query_shown = "";
$error       = "";

if (isset($_GET['q']) && $_GET['q'] !== '') {
    $q = $_GET['q'];

    // VULNERABLE: direct string interpolation
    $sql         = "SELECT username, email, role FROM users WHERE username='$q'";
    $query_shown = $sql;
    $result      = mysqli_query($db, $sql);

    if ($result) {
        while ($row = mysqli_fetch_assoc($result)) {
            $results[] = $row;
        }
    } else {
        $error = mysqli_error($db);
    }
}
?>
<!DOCTYPE html>
<html>
<head><title>User Search</title></head>
<body>
  <h2>User Search</h2>
  <form method="GET">
    <input type="text" name="q" placeholder="Search username..."
           value="<?= htmlspecialchars($_GET['q'] ?? '') ?>" />
    <button type="submit">Search</button>
  </form>

  <?php if ($query_shown): ?>
    <p style="color:grey;font-size:12px;">Query: <?= $query_shown ?></p>
  <?php endif; ?>

  <?php if ($error): ?>
    <p style="color:red;">DB Error: <?= $error ?></p>
  <?php endif; ?>

  <?php if ($results): ?>
    <table border="1" cellpadding="8">
      <tr><th>Username</th><th>Email</th><th>Role</th></tr>
      <?php foreach ($results as $r): ?>
        <tr>
          <td><?= $r['username'] ?></td>
          <td><?= $r['email'] ?></td>
          <td><?= $r['role'] ?></td>
        </tr>
      <?php endforeach; ?>
    </table>
  <?php elseif ($query_shown): ?>
    <p>No results found.</p>
  <?php endif; ?>
</body>
</html>
