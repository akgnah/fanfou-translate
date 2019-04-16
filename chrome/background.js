var DefaultOptions = {
    "enable": ["checked", true],
    "hyphen": ["checked", true],
    "remind": ["checked", false],
    "source": ["value", "youdao"],
    "sweep": ["checked", false],
    "click": ["checked", true],
    "ssid": ["value", null]
};

if (localStorage["Options"] === undefined) {
    localStorage["Options"] = JSON.stringify(DefaultOptions);
}

function readOpention(key) {
    return (JSON.parse(localStorage["Options"]))[key][1];
}

function onRequest(request, sender, sendResponse) {
    if (request.action == "init") {
        sendResponse({Options: localStorage["Options"]});
    }
    if (request.action == "translate") {
        fetchTranslate(request.word, sendResponse);
    }
}

function fetchTranslate(word, sendResponse) {
    var xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var data = xhr.response;

            if(data !== null) {
                sendResponse(JSON.parse(data));
            }
        }
    };

    var ssid = readOpention("remind")? readOpention("ssid") || "public": "public";
    var source = "&source=" + readOpention("source");
    var url = "http://127.0.0.1:5000/fanyi?word=" + encodeURIComponent(word) + "&ssid=" + ssid + source;

    xhr.open("GET", url, true);
    xhr.send();
}

chrome.extension.onRequest.addListener(onRequest);
chrome.browserAction.setIcon({path: readOpention('enable')? "icon_dict.png": "icon_nodict.png"});  // Init Icon