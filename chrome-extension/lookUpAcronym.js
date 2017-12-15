// lookUpAcronym.js
//
// This file is the background script for the Chrome extension.
// It handles the creation of the context menu and the highlevel
// "look up acronym" call.

// add "Look up acronym" as option in "right click" menu
chrome.contextMenus.create(
    {
        title: "Look up acronym",
        contexts: ['selection'],
        onclick: lookUpAcronym
    }
);

// look up the meaning of the acronyms in the selected text
function lookUpAcronym(info, tab) {
    // pass selected text to gunicorn server
    $.post("http://127.0.0.1:8000/", {selection:info.selectionText},
           function (response) {
	       chrome.tabs.query({active:true, currentWindow: true}, 
				 function(tabs) {
				     // send response to the content script to be displayed
				     chrome.tabs.sendMessage(tabs[0].id, {method: "displayMeaning", meaning: response});
				 });
	   });
}
