<?php 

require_once "../include/myview.php";

$t = new MyView();
$t->title = "Unidata IDD Database Demonstration";

$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/jquery-datatables/1.10.16/datatables.min.css" />
<style>
input {
  text-transform: uppercase;
}
</style>
EOM;

$t->jsextra = <<<EOM
<script src="/vendor/jquery-datatables/1.10.16/datatables.min.js"></script>
<script src="app.js"></script>
EOM;

$t->content = <<<EOM

<h3>Unidata IDD Database Demonstration</h3>

<p>This is an unofficial demonstration app showing a query interface into a
database of LDM IDD Products.  This application was driven by a
<a href="https://github.com/Unidata/unidata-usercomm/issues/14">Unidata Users Committee idea</a>
to provide some details on what flows over the IDD. Everything you see here
is in flux and could use your feedback!</p>

<form id="searchform">
<div class="row">

<div class="col-md-3">
  <div class="form-group">
    <label for="wmo_ttaaii"><i class="glyphicon glyphicon-search"></i> WMO TTAAII</label>
    <input type="text" class="form-control" id="wmo_ttaaii" placeholder="FXUS63">
  </div>
</div>

<div class="col-md-3">
  <div class="form-group">
    <label for="wmo_source"><i class="glyphicon glyphicon-search"></i> WMO Source</label>
    <input type="text" class="form-control" id="wmo_source" placeholder="KDMX">
  </div>
</div>

<div class="col-md-3">
  <div class="form-group">
    <label for="awips_id"><i class="glyphicon glyphicon-search"></i> AWIPS ID</label>
    <input type="text" class="form-control" id="awips_id" placeholder="AFDDMX">
  </div>
</div>


</form>

<div class="row">
<div class="col-xs-12">
<table id="res" data-order='[[ 0, "desc" ]]'>
<thead>
<tr><th>Received At</th>
<th>Ingested At</th>
<th>WMO Valid At</th>
<th>Size</th><th>TTAAII</th><th>Source</th>
<th>AWIPS ID</th><th>LDM Product ID</th>
</tr>
</thead>
<tbody>

</tbody>
</table>
</div>

EOM;


$t->render("single.phtml");

?>