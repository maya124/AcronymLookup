// showMeaning.js
//
// This file is the content script for the Chrome extension.
// It listens for requests from the background script, then
// modifies the current document as necessary (in this case
// by displaying the correct meaning for the highlighted
// acronyms.

// listen for a message from the background script
if (!chrome.runtime.onMessage.hasListener(listener)) {
    chrome.runtime.onMessage.addListener(listener);
}

// display the meaning of the acronym (as taken from |request|)
function listener(request, sender, sendResponse) {
    if (request.method == "displayMeaning") {

	// if there is text selected
	var sel = window.getSelection();
	if (sel) {
            if (sel.rangeCount) {
		// insert a popup with the corresponding meaning
		var range = sel.getRangeAt(0).cloneRange();
		var popup = document.createElement("div");
		popup.className = "popup";
		range.insertNode(popup);
		$(".popup").html(request.meaning);
		$(".popup").show();
		sel.removeAllRanges();
            }
	}
    }
}

// remove the popup if the user clicks away from it
$(document).click(
    function() {
        var sel = window.getSelection()
        if(sel){
            $(".popup").remove();
        }
    }
);
