const QR_CODE_URL = 'qr-code';
const FETCH_HEADERS = { 'X-Fetch': 'true' };
const QR_CODE_ELEMENT_ID = 'qr-code';
const EXPIRY_MSG_ELEMENT_ID = 'expiry-msg';
const QR_CODE_EXPIRY_TIME = 30; // seconds

async function getQRCode() {
    try {
        const response = await fetch(QR_CODE_URL, { headers: FETCH_HEADERS });
        if (!response.ok) {
            throw new Error('Failed to get QR code');
        }
        const data = await response.text();
        return `data:image/png;base64,${data}`;
    } catch (error) {
        console.error('Error fetching QR code:', error);
        throw error;
    }
}

function updateQRCode() {
    let expiryTime = 0;
    const qrCodeElement = document.getElementById(QR_CODE_ELEMENT_ID);
    const expiryMsgElement = document.getElementById(EXPIRY_MSG_ELEMENT_ID);

    const refreshQRCode = async () => {
        try {
            const qr = await getQRCode();
            qrCodeElement.src = qr;
            expiryTime = QR_CODE_EXPIRY_TIME;
            refreshExpiryMessage();

            const intervalId = setInterval(async () => {
                expiryTime--;
                refreshExpiryMessage();
                if (expiryTime <= 0) {
                    clearInterval(intervalId);
                    await refreshQRCode();
                }
            }, 1000);
        } catch (error) {
            console.error('Error refreshing QR code:', error);
        }
    }

    const refreshExpiryMessage = () => {
        if (expiryTime <= 0) {
            expiryMsgElement.textContent = 'Fetching new QR code';
        } else {
            expiryMsgElement.textContent = `This QR code expires in ${expiryTime} second${expiryTime === 1 ? '' : 's'}`;
        }
    }

    refreshQRCode();
}

document.addEventListener('DOMContentLoaded', updateQRCode);