function autoReload(value) {
    var timeID = setTimeout("location.href= '/'", value)
}

// ---------- order/check.html
function checkStatusPayment() {
    var pay = document.getElementById("id_Pagamento");
    var sel_pay = pay.options[pay.selectedIndex].text;
    var card = document.getElementById("id_Carta");
    if (sel_pay == "Carta di credito")
        card.disabled = false;
    else
        card.disabled = true;
}

function checkValues() {
    var pay = document.getElementById("id_Pagamento");
    var sel_pay = pay.options[pay.selectedIndex].text;
    var card = document.getElementById("id_Carta");
    var sel_card = card.options[card.selectedIndex].text;
    var errorCard = document.getElementById("id_ErrorCard");
    var button = document.getElementById("id_SubmitForm");
    var time = document.getElementById("id_Orario");
    var sel_time = time.value;
    var errorTime = document.getElementById("id_ErrorTime");
    if (sel_time == '') {
        errorTime.hidden = false;
        button.disabled = true;
    } else if (sel_time > time.min && sel_time < time.max) {
        errorTime.hidden = true;
        button.disabled = true;
        if (sel_pay == "Carta di credito") {
            if (sel_card == '---------') {
                errorCard.hidden = false;
                button.disabled = true;
            } else {
                errorCard.hidden = true;
                button.disabled = false;
            }
        } else
            button.disabled = false;
    } else {
        errorTime.hidden = false;
        button.disabled = true;
    }
}

// ---------------- order/placed_order.html
function stampa() {
    var but = document.getElementById('id_PrintButton');
    but.hidden = true;
    print();
    but.hidden = false;
}