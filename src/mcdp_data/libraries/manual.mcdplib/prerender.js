console.log('Loading libraries..');
var mjAPI = require("mathjax-node/lib/mj-page.js");
var jsdom = require("jsdom").jsdom;
var fs = require('fs');

manual = process.argv[2];
manual_out = process.argv[3];
// var d = '/Volumes/1604-mcdp/data/env_mcdp/src/mcdp/src/mcdp_data/libraries/manual.mcdplib/'
// var manual = d + 'out-html/manual.html';
// var manual_out = d + 'out-html/manual_prerender.html';

console.log('reading ' + manual);
var data = fs.readFileSync(manual, 'utf8');
var document = jsdom(data); 


console.log('rendering...')

mjAPI.start();
mjAPI.typeset({
  html: document.body.innerHTML,
  renderer: "NativeMML",
  renderer: "SVG",
  // "output/SVG",
  inputs: ["TeX"],
  xmlns: "mml"
}, function(result) {
    console.log('rendering done.')
  "use strict";
  document.body.innerHTML = result.html;
  var h = document.documentElement.outerHTML.replace(/^(\n|\s)*/,"");
  var HTML = "<!DOCTYPE html>\n" + h;
  fs.writeFileSync(manual_out, HTML);
  console.log('written to ' + manual_out);
});




