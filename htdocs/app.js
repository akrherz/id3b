var DT;
var request;
var wto;

function update(){
	var awips_id = $("#awips_id").val();
	var wmo_source = $("#wmo_source").val();
	var wmo_ttaaii = $("#wmo_ttaaii").val();
	request = $.ajax({
		url: '/services/search.py',
		data: {
			awips_id: awips_id,
			wmo_source: wmo_source,
			wmo_ttaaii: wmo_ttaaii
		},
		method: 'GET',
		dataType: 'json',
		beforeSend: function(){
			if (request != null) request.abort();
		},
		success: function(res){
			$("#generated_at").html(res.generated_at);
			$("#generation_time").html(res['generation_time[secs]']);
			DT.clear()
			$.each(res.products, function(idx, product){
				DT.row.add([
					product.entered_at, product.valid_at,
					product.wmo_valid_at, product.size,
					product.wmo_ttaaii, product.wmo_source,
					product.awips_id, product.product_id]);
			});
			DT.draw();
		}
	});
}

function buildUI(){
	DT = $("#res").DataTable();
	$("#searchform input[type='text']").on('keyup', function(e){
		var value = $(this).val();
		if (value != $(this).data('current')){
			$(this).data('current', value);
			clearTimeout(wto);
			wto = setTimeout(function(){
				update();
			}, 200); // 200ms of delay before we act on some change
		}
	});
}


$(function(){
	buildUI();
});
