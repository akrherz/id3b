var DT;
var requestController;
var wto;

function showSpinner() {
  var el = document.getElementById("spinner");
  if (el) el.style.display = "";
}

function hideSpinner() {
  var el = document.getElementById("spinner");
  if (el) el.style.display = "none";
}

function update() {
  showSpinner();
  var awips_id = (document.getElementById("awips_id") || {}).value || "";
  var wmo_source = (document.getElementById("wmo_source") || {}).value || "";
  var wmo_ttaaii = (document.getElementById("wmo_ttaaii") || {}).value || "";
  var product_id = (document.getElementById("product_id") || {}).value || "";

  // abort prior request if any
  if (requestController) requestController.abort();
  requestController = new AbortController();

  var params = new URLSearchParams({
    awips_id: awips_id,
    wmo_source: wmo_source,
    wmo_ttaaii: wmo_ttaaii,
    product_id: product_id,
  });

  fetch('/services/search.py?' + params.toString(), { signal: requestController.signal })
    .then(function (resp) {
      if (!resp.ok) throw new Error('Network response was not ok');
      return resp.json();
    })
    .then(function (res) {
      hideSpinner();
      var gen = document.getElementById('generated_at');
      if (gen) gen.innerHTML = res.generated_at || '';
      var gt = document.getElementById('generation_time');
      if (gt) gt.innerHTML = res['generation_time[secs]'] || '';

      // If DT supports DataTables API use it, otherwise manipulate the tbody directly
      if (DT && typeof DT.clear === 'function' && typeof DT.row === 'function') {
        DT.clear();
        (res.products || []).forEach(function (product) {
          DT.row.add([
            product.feedtype,
            product.entered_at,
            product.valid_at,
            product.wmo_valid_at,
            product.size,
            product.wmo_ttaaii,
            product.wmo_source,
            product.awips_id,
            product.product_id,
          ]);
        });
        DT.draw();
      } else {
        var tbody = document.querySelector('#res tbody');
        if (tbody) {
          // clear
          while (tbody.firstChild) tbody.removeChild(tbody.firstChild);
          (res.products || []).forEach(function (product) {
            var tr = document.createElement('tr');
            [
              product.feedtype,
              product.entered_at,
              product.valid_at,
              product.wmo_valid_at,
              product.size,
              product.wmo_ttaaii,
              product.wmo_source,
              product.awips_id,
              product.product_id,
            ].forEach(function (v) {
              var td = document.createElement('td');
              td.textContent = v == null ? '' : v;
              tr.appendChild(td);
            });
            tbody.appendChild(tr);
          });
        }
      }
    })
    .catch(function (err) {
      if (err.name === 'AbortError') return; // expected on abort
      hideSpinner();
      console.error('Request failed', err);
    });
}

function buildUI() {
  hideSpinner();

  // Initialize DataTables if available. Some environments include the jQuery DataTables
  // plugin; prefer the jQuery-based API when present, otherwise try a vanilla constructor.
  if (window.jQuery && window.jQuery.fn && window.jQuery.fn.DataTable) {
    try {
      DT = window.jQuery('#res').DataTable();
    } catch (e) {
      DT = null;
    }
  } else if (typeof DataTable === 'function') {
    try {
      DT = new DataTable('#res');
    } catch (e) {
      DT = null;
    }
  } else {
    DT = null;
  }

  // keyup handler for inputs in the search form
  var inputs = document.querySelectorAll('#searchform input[type="text"]');
  inputs.forEach(function (inp) {
    inp.addEventListener('keyup', function (e) {
      var value = inp.value;
      if (value !== inp.dataset.current) {
        inp.dataset.current = value;
        clearTimeout(wto);
        wto = setTimeout(function () { update(); }, 200);
      }
    });
  });

  var mrf = document.getElementById('mrf');
  if (mrf) {
    mrf.addEventListener('click', function (e) {
      update();
      if (e.currentTarget && typeof e.currentTarget.blur === 'function') e.currentTarget.blur();
    });
  }
}

document.addEventListener('DOMContentLoaded', function () { buildUI(); });
