var DefaultOptions = {
    "enable": ["checked", true],
    "hyphen": ["checked", true],
    "remind": ["checked", true],
    "source": ["value", "youdao"],
    "sweep": ["checked", false],
    "click": ["checked", true],
    "ssid": ["value", null]
};

if (localStorage["Options"] === undefined) {
    localStorage["Options"] = JSON.stringify(DefaultOptions);
}

function saveOptions() {
    var Options = JSON.parse(localStorage["Options"]);

	for (var key in Options) {
        if (Options[key][0] == "checked") {
            Options[key][1] = document.getElementById(key).checked;
        } else {
            Options[key][1] = document.getElementById(key).value.trim();
        }
    }

    localStorage["Options"] = JSON.stringify(Options);
    updateStatus();
}

function restoreOptions() {
    var Options = JSON.parse(localStorage["Options"]);

    for (var key in Options) {
        if (Options[key][0] == "checked") {
            document.getElementById(key).checked = Options[key][1];
        } else {
            document.getElementById(key).value = Options[key][1];
        }
    }

    updateStatus();
}

function readOpention(key) {
    return (JSON.parse(localStorage["Options"]))[key][1];
}

function updateStatus() {
	if (document.getElementById('enable').checked) {
        showDiv('enable');
		chrome.browserAction.setIcon({path: "icon_dict.png"});
	} else {
        hideDiv('enable');
		chrome.browserAction.setIcon({path: "icon_nodict.png"});
	}
}

function hideDiv(divname) {
    var div = document.getElementsByClassName(divname);

    for (var i = 0; i < div.length; i++) {
        div[i].style.display = "none";
    }
}

function showDiv(divname) {
    var div = document.getElementsByClassName(divname);

    for (var i = 0; i < div.length; i++) {
        div[i].style.display = "block";
    }
}

function goIssue() {
    window.open("https://github.com/akgnah/fanfou-translate");
}

function goAbout() {
    window.open("https://setq.me/fanyi");
}

function mainQuery(event) {
    if (event.type != "click" && event.keyCode != 13) {
        return;
    }

    var word = document.getElementById("word").value.trim();

    if (!word) {
        document.getElementById('word').focus();
        document.getElementById("word").value = "";
        return;
    }

    var xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var data = xhr.response;

            if(data !== null) {
                getTrans(JSON.parse(data));
            }
        }
    };

    var ssid = readOpention("remind")? readOpention("ssid") || "public": "public";
    var source = "&source=" + readOpention("source");
    var url = "http://127.0.0.1:5000/fanyi?word=" + encodeURIComponent(word) + "&ssid=" + ssid + source;

    xhr.open("GET", url, true);
    xhr.send();
}

function getTrans(data) {
    var result = "";

    hideDiv("opt");

    if (data["trans"].trim() != "404 Not Found") {
        if (readOpention("hyphen") && data["word"] != data["hyphen"]) {
            result += "<strong>音节划分：</strong><br>" + data["hyphen"] + "<br>";
        }
        result += "<strong>基本释义：</strong><br>";
    }

    for (var item of data["trans"].split("\n")) {
        result += item + "<br>";
    }

    document.getElementById('result').innerHTML = result;
}

window.onload = function() {
    restoreOptions();
    document.getElementById("word").focus();
    document.getElementById("enable").onclick = saveOptions;
    document.getElementById("hyphen").onclick = saveOptions;
    document.getElementById("remind").onclick = saveOptions;
    document.getElementById("source").onchange = saveOptions;
    document.getElementById("sweep").onclick = saveOptions;
    document.getElementById("click").onclick = saveOptions;
    document.getElementById("ssid").onblur = saveOptions;
    document.getElementById("issue").onclick = goIssue;
    document.getElementById("about").onclick = goAbout;
    document.getElementById("query").onclick = mainQuery;
    document.getElementById("word").onkeydown = mainQuery;
};