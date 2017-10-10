var DT;

function buildUI(){
	DT = $("#res").DataTable();
	$("#searchform input[type='text']").on('keyup', function(event){
		if(event.which == 13) return false;
		var awips_id = $("#awips_id").val();
		var wmo_source = $("#wmo_source").val();
		var wmo_ttaaii = $("#wmo_ttaaii").val();
		$.ajax({
			url: '/services/search.py',
			data: {
				awips_id: awips_id,
				wmo_source: wmo_source,
				wmo_ttaaii: wmo_ttaaii
			},
			method: 'GET',
			dataType: 'json',
			success: function(res){
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
	});
}


$(function(){
	buildUI();
});
