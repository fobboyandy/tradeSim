<?php
if(!empty($_GET['username']))
{
	if(isset($_GET['Log']))
	{
		$usernameString = urlencode($_GET['username']);
		header("Location:data/" . $usernameString . ".html");
	}
	$usernameString = urlencode($_GET['username']);
	if(isset($_GET['Refresh']))
		header("Location:portfolio.php?username=" . $usernameString);
		
	$scriptPath = "\"D:\\Program Files (x86)\\Ampps\\www\\tradesim\\scripts\\webTraderSim.py\"";
	$usernameString = urlencode($_GET['username']);
	$actionString = urlencode($_GET['action']);
	$stockNameString = urlencode($_GET['stockName']);
	$sharesString = urldecode($_GET['shares']);
	
	if($actionString == "close")
		$sharesString = "0";
	
	$command = $scriptPath . " " . $usernameString . " " .  $actionString . " " . $stockNameString . " " . $sharesString;
	system($command);
}




?>

<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset"utf-8"/>
	<title>Trade Sim: Portfolio</title>
</head>
<body>


<form action="" method="get">
<input type ='hidden' name='username' value='<?php echo $usernameString; ?>'>
<input type='submit' name='Refresh' value='Refresh Portfolio'/>
</form>

<br></br>
<br></br>
<br></br>
<text><b>Order</b></text>
<br></br>
<form action="" method="get">
<input type ='hidden' name='username' value='<?php echo $usernameString; ?>'>
<Input type = 'Radio' Name ='action' value= 'buy'
>Buy
<Input type = 'Radio' Name ='action' value= 'sell' 
>Sell
<Input type = 'Radio' Name ='action' value= 'buyCover' 
>Buy to Cover
<Input type = 'Radio' Name ='action' value= 'sellShort' 
>Sell to Short 
<Input type = 'Radio' Name ='action' value= 'close' 
>Close Position 
<br></br>
<input type='text' name='stockName' placeholder='Stock Name'/>
<input type='text' name='shares' placeholder='Number of Shares'/>
<!--Currently not supporting limits
<input type='text' name='price' placeholder='Limit Price'/>
-->
<input type='submit' name='Submit' value='Submit'/>
</form>

<form action="" method="get">
<input type ='hidden' name='username' value='<?php echo $usernameString; ?>'>
<input type='submit' name='Log' value='Review Log'/>
</form>




</body>

</html>