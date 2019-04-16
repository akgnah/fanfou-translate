var pos;
var Options = null;

function isEnglish(str) {
    return /^[a-zA-Z-'\.\s]+$/.test(str);
}

function onSweepTrans(event) {
    var frame = document.getElementById('setq-popup');
    var sel = window.getSelection();
    var word = sel.toString().trim();

    if (frame && !frame.contains(event.target)) {
        frame.style.display = "none";
    }

    if (frame && frame.style.display != "none" || event.button !== 0) {
        return;
    }

    if (!isEnglish(word)) {
        return;
    } else {
        pos = sel.getRangeAt(0).getBoundingClientRect();
    }

    chrome.extension.sendRequest({'action': 'translate' , 'word': word}, getTrans);
}

function onClickTrans(event) {
    var button = document.getElementById('setq-btn');
    var frame = document.getElementById('setq-popup');
    var sel = window.getSelection();
    var word = sel.toString().trim();

    if (event.target === button) {
        button.style.display = "none";
        chrome.extension.sendRequest({'action': 'translate' , 'word': word}, getTrans);
        return;
    }

    if (frame && !frame.contains(event.target)) {
        frame.style.display = "none";
    }

    if (button && button.style.display != "none") {
        button.style.display = "none";
    }

    if (!isEnglish(word)) {
        return;
    } else {
        pos = sel.getRangeAt(0).getBoundingClientRect();
    }

    if (!button) {
        button = document.createElement('img');
        button.id = "setq-btn";
        button.src = chrome.extension.getURL("query.png");
        document.body.style.position = "static";
        document.body.appendChild(button);
    }

    button.style.left = pos.right + window.pageXOffset - 20 + "px";
    button.style.top = pos.bottom + window.pageYOffset + 5 + "px";
    button.style.display = "block";
}

function clearSelection(event) {
    var button = document.getElementById('setq-btn');

    if (event.target != button && event.button === 0) {
        document.getSelection().removeAllRanges();
    }
}

function createPopup(result) {
    var width = 250;
    var height = 150;
    var frameLeft = 0;
    var frameTop = 0;
    var frame = document.getElementById('setq-popup');

    if (!frame) {
        frame = document.createElement('div');
        frame.id = "setq-popup";
        frame.style.minHeight = height + "px";
        frame.style.width = width + "px";
        document.body.style.position = "static";
        document.body.appendChild(frame);
    }

    if (pos.left + width < document.body.clientWidth) {
        frameLeft = pos.left + window.pageXOffset;
    } else {
        frameLeft = pos.left + window.pageXOffset - width;
    }

    if (pos.bottom + height + 5 < document.body.clientHeight || height + 5 > document.body.clientHeight) {
        frameTop = pos.bottom + window.pageYOffset + 5;
    } else {
        frameTop = pos.top + window.pageYOffset - height - 5;
    }

    frame.style.left = frameLeft + "px";
    frame.style.top = frameTop + "px";
    frame.style.display = "block";
    frame.innerHTML = result;

    var audioBtn = document.getElementById('setq-audio-btn');
    
    if (audioBtn) {
        audioBtn.addEventListener('mousedown', function() {
            var audio = document.getElementById('setq-audio');
            audio.pause();
            audio.src = 'https://dict.youdao.com/dictvoice?audio=' + audio.innerText + '&type=1'
            audio.play();
        }, true);
    }
}

function getTrans(data) {
    var result = '<p class="setq-text"><span class="setq-word">' + data["word"] + "</span>";

    if (data["trans"].trim() != "404 Not Found") {
        if (data["pho"]) {
            result += '<span class="setq-phonetic">[' + data["pho"] + ']</span>';
        }
        result += '<audio id="setq-audio">' + data["word"] + '</audio>';
        result += '<img src="' + chrome.extension.getURL("speech.png") + '" id="setq-audio-btn"></p>';
        if (readOpention("hyphen") && data["word"] != data["hyphen"]) {
            result += '<p class="setq-text"><span class="setq-info">音节划分</span><br>' + data["hyphen"] + "</p>";
        }
        result += '<p class="setq-text"><span class="setq-info">基本释义</span><br>';
    } else {
        result += '</p><p class="setq-text">';
    }

    for (var item of data["trans"].split("\n")) {
        result += item + "<br>";
    }

    result = result.slice(0, -4) + "</p>";

    createPopup(result);
}

function readOpention(key) {
    return Options[key][1];
}

chrome.extension.sendRequest({ action: "init" },
    function(response) {
        if (response.Options) {
            Options = JSON.parse(response.Options);
        }
        if (readOpention("enable")) {
            if (readOpention("sweep")) {
                document.addEventListener('mouseup', onSweepTrans, true);
            } else {
                document.addEventListener('mouseup', onClickTrans, true);
            }
            document.addEventListener('mousedown', clearSelection, true);
        }
    }
);