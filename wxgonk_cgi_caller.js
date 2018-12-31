/**
 * This file makes an XMLHttpRequest to wxgonk.py, which is then run and its 
 * output returned using CGI.
 *
 * @author Andrew Geist
 *
 * Last updated Mon Dec 31 17:52:56 2018
 */

'use strict';

function run_wxgonk(){
    var url="wxgonk.py";
    var xhr=null;
    if (window.XMLHttpRequest){
        xhr = new XMLHttpRequest();
    } else if (window.ActiveXObject){
        xhr = new ActiveXObject("Microsoft.XMLHTTP");
    }
    xhr.onreadystatechange = function(){
        if (xhr.readyState == XMLHttpRequest.DONE){
            document.getElementById("wxgonk-results").innerHTML=xhr.responseText;
        }
    }
    xhr.open("GET",url,true);
    xhr.send(null);
}

window.onload = run_wxgonk;
