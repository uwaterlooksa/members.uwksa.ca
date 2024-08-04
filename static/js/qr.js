function getQRCode() {
    return fetch('qr-code', {
        headers: {
            'X-Fetch': 'true'
        },
    }).then(response => {
        if (!response.ok) {
            throw new Error('Failed to get QR code');
        }
        return response.text();
    }).then(data => `data:image/png;base64,${data}`);
}

function updateQRCode() {
    let expiryTime = 0;

    function refreshQRCode() {
        getQRCode().then(qr => {
            document.getElementById('qr-code').src = qr;
            expiryTime = 30;
            refreshExpiryMessage();
        }).catch(error => {
            console.log(error);
        });
    }

    function refreshExpiryMessage() {
        if (expiryTime <= 0) {
            document.getElementById('expiry-msg').textContent = 'Fetching new QR code';
        } else {
            document.getElementById('expiry-msg').textContent = 'This QR code expires in ' + expiryTime + ' second' + (expiryTime == 1 ? '' : 's');
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

document.addEventListener('DOMContentLoaded', () => {
    updateQRCode();
});