chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.action === 'fetchApiData') {
    const currentUrl = request.url;
    const isRoundTrip = request.roundTrip
    // API endpoint URL
    const apiEndpoint = "http://0.0.0.0:8000/";
  
    fetch(apiEndpoint, {
        method: 'POST', 
        headers: {
            'Content-type': 'application/json'
        },
        body: JSON.stringify({url: currentUrl, roundTrip: isRoundTrip})
    })
    .then(response => response.json())
    .then(data => {
        const maps_url = data.google_maps_url;
        if (maps_url) {
            chrome.tabs.create({url: maps_url});
        }
    })
  }
});