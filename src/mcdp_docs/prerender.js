#!/usr/bin/env node
// console.log('Loading libraries..');
require('MathJax-node')

var mjAPI = require("MathJax-node/lib/mj-page.js");
var jsdom = require("jsdom").jsdom;
var fs = require('fs');

manual = process.argv[2];
manual_out = process.argv[3];
// var d = '/Volumes/1604-mcdp/data/env_mcdp/src/mcdp/src/mcdp_data/libraries/manual.mcdplib/'
// var manual = d + 'out-html/manual.html';
// var manual_out = d + 'out-html/manual_prerender.html';

// console.log('reading ' + manual);
var data = fs.readFileSync(manual, 'utf8');
var document = jsdom(data);


console.log('rendering...');
// need to add:
// function SetRenderer(renderer) {
//   if (renderer === "IMG" || renderer === "PNG") renderer = "SVG";
//     MathJax.Hub.Config({
//     SVG: {
//       scale: 300
//     }
//   });

//   return MathJax.Hub.setRenderer(renderer);
// }

// mjAPI.SetRenderer=SetRenderer;

mjAPI.start();
// window.MathJax.Hub.Config({
//     SVG: {
//       scale: 300
//     }
// });
console.log('started');

mjAPI.typeset({
  'html': document.body.innerHTML,
  // renderer: "NativeMML", // problme: sometimes doesnt work in prince for single docs; problem: ugly
  'renderer': "SVG", // problem: too large
  // 'renderer': "PNG", // no
  // "output/SVG",
  'inputs': ["TeX"],
  'xmlns': "mml",
}, function(result) {
    console.log('rendering done.')
  "use strict";
  // document.body.innerHTML = result.html;
  // var h = document.documentElement.outerHTML.replace(/^(\n|\s)*/,"");
  // var HTML = "<!DOCTYPE html>\n" + h;
  HTML = result.html;
  fs.writeFileSync(manual_out, HTML);
  // console.log('written to ' + manual_out);
  console.log('success');
});
