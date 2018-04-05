<?php
if(!empty($_GET['username']))
{
	$usernameString = urlencode($_GET['username']);
	$command = "\"D:\\Program Files (x86)\\Ampps\\www\\tradesim\\scripts\\displayPortfolio.py\" " . $usernameString;
	$output = exec($command);
	print($output);
	header("Location: portfolio.php"."?username=". $usernameString);
}
?>


<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset"utf-8"/>
	<title>Trade Sim: Login</title>
</head>
<body>

<form action="">
Username: 
<input type='text' name='username'/>
<input type='submit'/>
</form>

</body>

</html>