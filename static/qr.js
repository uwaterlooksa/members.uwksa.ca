function docReady(fn) {
    // see if DOM is already available
    if (document.readyState === "complete"
        || document.readyState === "interactive") {
        // call on next available tick
        setTimeout(fn, 1);
    } else {
        document.addEventListener("DOMContentLoaded", fn);
    }
}

docReady(() => {
    Html5Qrcode.getCameras().then(devices => {
        if (devices && devices.length) {
            const html5QrCode = new Html5Qrcode("reader", { formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE] });
            html5QrCode.start(
                { facingMode: { exact: "environment" } },
                {
                    fps: 10,
                    aspectRatio: 1.0,
                    videoConstraints: {
                        width: 3000,
                        height: 3000,
                        facingMode: "environment",
                    }
                },
                qrCodeMessage => {
                    // console.log(qrCodeMessage);
                    html5QrCode.stop();
                    window.location.href = qrCodeMessage;
                },
                errorMessage => {
                    // console.log(errorMessage);
                }
            )
        }
    }).catch(err => {
        console.log(err);
    });
}
);