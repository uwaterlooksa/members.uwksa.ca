function getQRCode() {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: '/qr-code',
            method: 'GET',
            success: function (data) {
                const qrCode = 'data:image/png;base64,' + data;
                resolve(qrCode);
            },
            error: function (error) {
                reject(error);
            }
        });
    });
}

function updateQRCode() {
    let expiryTime = 0;

    function refreshQRCode() {
        getQRCode().then(qr => {
            $('#qr-code').attr('src', qr);
            expiryTime = 30;
            refreshExpiryMessage();
        }).catch(error => {
            console.log(error);
        });
    }

    function refreshExpiryMessage() {
        if (expiryTime <= 0) {
            $('#expiry-msg').text('Fetching new QR code');
        } else {
            $('#expiry-msg').text('This QR code expires in ' + expiryTime + ' second' + (expiryTime == 1 ? '' : 's'));
        }
    }

    refreshQRCode();

    setInterval(function () {
        if (expiryTime == 1) {
            refreshQRCode();
        }
        expiryTime--;
        refreshExpiryMessage();
    }, 1000);
}

$(document).ready(function () {
    updateQRCode();
});