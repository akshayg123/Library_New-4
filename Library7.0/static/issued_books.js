function generateQRCode(student_id, book_id, date_of_issue, return_date) {
    var data = student_id + ' ' + book_id + ' ' + date_of_issue + ' ' + return_date;
    var qrcodeElement = document.getElementById('qrcode' + student_id + book_id);
    
    // Clear the div before generating a new QR code
    while (qrcodeElement.firstChild) {
        qrcodeElement.removeChild(qrcodeElement.firstChild);
    }
    
    var qrcode = new QRCode(qrcodeElement, {
        text: data,
        width: 128,
        height: 128
    });
    
    // Add the close button
    var closeButton = document.createElement('span');
    closeButton.textContent = 'X';
    closeButton.style.cursor = 'pointer';
    closeButton.onclick = function() { removeQRCode('qrcode' + student_id + book_id); };
    qrcodeElement.appendChild(closeButton);
    
    qrcodeElement.style.display = 'block';
}

function removeQRCode(id) {
    var element = document.getElementById(id);
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
    element.style.display = 'none';
}
