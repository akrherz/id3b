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
<script src="app.js?v=2"></script>
EOM;

$t->content = <<<EOM

<h3>Unidata IDD Database Demonstration</h3>

<p>This is an unofficial demonstration app showing a query interface into a
database of LDM IDD Products.  This application was driven by a
<a href="https://github.com/Unidata/unidata-usercomm/issues/14">Unidata Users Committee idea</a>
to provide some details on what flows over the IDD. Everything you see here
is in flux and could use <a href="https://github.com/akrherz/id3b/issues">your feedback</a>! This database is based on IDD node at Iowa State
of <code>metfs1.agron.iastate.edu</code> and <strong>does not feed the full suite of products</strong> from Unidata.
You can find the exact upstreams with its <a href="https://github.com/akrherz/ldmconfig/blob/master/metfs1/ldmd.conf">ldmd.conf file</a>.</p>

<form id="searchform">
<div class="row">

<div class="col-md-3">
  <div class="form-group">
    <label for="wmo_ttaaii"><i class="glyphicon glyphicon-search"></i> WMO TTAAII</label>
    <input data-current="" type="text" class="form-control" id="wmo_ttaaii" placeholder="FXUS63">
  </div>
</div>

<div class="col-md-3">
  <div class="form-group">
    <label for="wmo_source"><i class="glyphicon glyphicon-search"></i> WMO Source</label>
    <input data-current="" type="text" class="form-control" id="wmo_source" placeholder="KDMX">
  </div>
</div>

<div class="col-md-3">
  <div class="form-group">
    <label for="awips_id"><i class="glyphicon glyphicon-search"></i> AWIPS ID</label>
    <input data-current="" type="text" class="form-control" id="awips_id" placeholder="AFDDMX">
  </div>
</div>

<div class="col-md-3">
  <button type="button" id="mrf" class="btn btn-default">Manual Table Refresh</button>
</div>
</div><!-- ./row -->

</form>

<div class="clearfix"></div>
<p>Results shown generated at <span id="generated_at">...</span> in <span id="generation_time">...</span> seconds.</p>


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