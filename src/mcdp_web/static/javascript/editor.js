/** Some utils for the editors **/


// used in edit_form_fancy.jinja2
function getCaretCharacterOffsetWithin(element) {
    var caretOffset = 0;
    if (typeof window.getSelection() != "undefined") {
        var range = window.getSelection().getRangeAt(0);
        var preCaretRange = range.cloneRange();
        preCaretRange.selectNodeContents(element);
        preCaretRange.setEnd(range.endContainer, range.endOffset);
        caretOffset = preCaretRange.toString().length;
    } else if (typeof document.selection != "undefined" && document.selection.type != "Control") {
        var textRange = document.selection.createRange();
        var preCaretTextRange = document.body.createTextRange();
        preCaretTextRange.moveToElementText(element);
        preCaretTextRange.setEndPoint("EndToEnd", textRange);
        caretOffset = preCaretTextRange.text.length;
    }
    return caretOffset;
}


// used in edit_form_fancy.jinja2
function get_elements(editor) {
  /* Returns a list of dictionary. The length is the size of the text() inside the editor.
    The k-th one is a dict of type {'char': i, 'text': textNode} 
    Meaning that the k-th character of the text is actually the i-th char in textNode.
    This is useful to place the caret at a specific place.
    */
  var walk_the_DOM = function walk(node, func) {
      func(node);
      node = node.firstChild;
      while (node) {
          walk(node, func);
          node = node.nextSibling;
      }
  };
  whole = '';
  elements = [];
  walk_the_DOM(editor, function(node) {
    s = node.nodeValue
    if (s != null) {
      whole = whole + s;

      for(i=0;i<s.length;i++) {
        w = {'char': i, 'text': node};
        elements.push(w);
      }
    } 
  });
  //console.log(whole);
  return elements;
}

// Disable/enable function
jQuery.fn.extend({
    disable: function() {
        return this.each(function() {
            this.disabled = true;
        });
    },
    enable: function() {
        return this.each(function() {
            this.disabled = false;
        });
    }
});


function getCaretPosition(editableDiv) {
  var caretPos = 0,sel, range;
  if (window.getSelection) {
    sel = window.getSelection();
    if (sel.rangeCount) {
      range = sel.getRangeAt(0);
      if (range.commonAncestorContainer.parentNode == editableDiv) {
        caretPos = range.endOffset;
      }
    }
  } else if (document.selection && document.selection.createRange) {
    range = document.selection.createRange();
    if (range.parentElement() == editableDiv) {
      var tempEl = document.createElement("span");
      editableDiv.insertBefore(tempEl, editableDiv.firstChild);
      var tempRange = range.duplicate();
      tempRange.moveToElementText(tempEl);
      tempRange.setEndPoint("EndToEnd", range);
      caretPos = tempRange.text.length;
    }
  }
  return caretPos;
}