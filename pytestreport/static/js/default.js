
output_list = Array();
/* level - 0:Summary; 1:Failed; 2:Skip; 3:All */

function showCase(level) {
    trs = document.getElementsByTagName("tr");
    for (var i = 0; i < trs.length; i++) {
        tr = trs[i];
        id = tr.id;

        if (level === 0 && tr.getAttribute('type') === 'case') {
            tr.className = 'hiddenRow';
        } else if (level === 1) {
            if (id.substr(0,2) === 'ft') {
                tr.className = '';
            } else if (tr.getAttribute('type') === 'case') {
                tr.className = 'hiddenRow';
            }
        } else if (level === 2) {
            if (id.substr(0,2) === 'et') {
                tr.className = '';
            } else if (tr.getAttribute('type') === 'case') {
                tr.className = 'hiddenRow';
            }
        } else if (level === 3) {
            if (id.substr(0,2) === 'st') {
                tr.className = '';
            } else if (tr.getAttribute('type') === 'case') {
                tr.className = 'hiddenRow';
            }
        } else if (level === 4 && tr.getAttribute('type') === 'case') {
            tr.className = '';
        }
    }
}

function showClassDetail(cid, count) {
    var tr_list = document.querySelectorAll('tr[cid='+cid+']');
    var toHide = 1;

    for (var i = 0; i < count; i++) {
        if (tr_list[i].className) {
            toHide = 0;
        }
    }
    for (var i = 0; i < count; i++) {
        if (toHide) {
            tr_list[i].className = 'hiddenRow';
        } else {
            tr_list[i].className = '';
        }
    }
}

function showTestDetail(div_id){
    var details_div = document.getElementById(div_id)
    var displayState = details_div.style.display
    // alert(displayState)
    if (displayState != 'block' ) {
        displayState = 'block'
        details_div.style.display = 'block'
    }
    else {
        details_div.style.display = 'none'
    }
}
function html_escape(s) {
    s = s.replace(/&/g,'&amp;');
    s = s.replace(/</g,'&lt;');
    s = s.replace(/>/g,'&gt;');
    return s;
}


