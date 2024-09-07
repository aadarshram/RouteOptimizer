document.addEventListener('DOMContentLoaded', function () {
    // Query for the currently active tab in the current window
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        const currentUrl = tabs[0].url;

        // Send the current URL to the background script
        document.getElementById('Optimize').addEventListener('click', function () {
            const roundTripValue = document.querySelector('input[name="roundTrip"]:checked').value;
            const isRoundTrip = roundTripValue === 'yes';
            chrome.runtime.sendMessage({ action: 'fetchApiData', url: currentUrl, roundTrip: isRoundTrip });
        });
    });
});
