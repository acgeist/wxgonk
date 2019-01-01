/**
 * This file makes an XMLHttpRequest to wxgonk.py, which is then run and its 
 * output returned using CGI.
 *
 * @author Andrew Geist
 *
 * Last updated Mon Dec 31 17:52:56 2018
 */

'use strict';

//TODO: add parameters to this function so command line arguments can be sent to 
//wxgonk.py.
function run_wxgonk(){
    var url="wxgonk.py";
    var xhr=null;
    if (window.XMLHttpRequest){
        xhr = new XMLHttpRequest();
    } else if (window.ActiveXObject){
        xhr = new ActiveXObject("Microsoft.XMLHTTP");
    }
    var timer = 0;
    setInterval(function(){
        if (xhr.readyState !== XMLHttpRequest.DONE){
            document.getElementById("wxgonk-results").innerHTML += ".";
            timer ++;
        } else {
            return;
        }
    }, 1000);
    xhr.onreadystatechange = function(){
        if (xhr.readyState == XMLHttpRequest.DONE){
            let str = '<p class="pilsung-text">Wxgonk ran in ' + timer + ' seconds.</p>';
            str += xhr.responseText;
            document.getElementById("wxgonk-results").innerHTML = str;
        }
    }
    xhr.open("GET",url,true);
    xhr.send(null);
}

window.onload = run_wxgonk;
