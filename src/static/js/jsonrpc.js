
// XMLHttpRequest code from http://en.wikipedia.org/wiki/XMLHttpRequest.
if( !window.XMLHttpRequest ) XMLHttpRequest = function()
{
  try{ return new ActiveXObject("Msxml2.XMLHTTP.6.0") }catch(e){}
  try{ return new ActiveXObject("Msxml2.XMLHTTP.3.0") }catch(e){}
  try{ return new ActiveXObject("Msxml2.XMLHTTP") }catch(e){}
  try{ return new ActiveXObject("Microsoft.XMLHTTP") }catch(e){}
  throw new Error("Could not find an XMLHttpRequest alternative.")
};

function JSONRPC(server) {
    this.server = server;
};

JSONRPC.prototype = {

    defaultErrback: function(requestId, exception) {
        alert(exception.name + ": "+ exeption.message);
    },

    defaultCallback: function(requestId, value) {
        alert(value);
    },

    callRemote: function(method, params, callback) {
        var body = JSON.stringify({
            'id': parseInt(Math.random()*100),
            'method': method,
            'params': params
        });
        var request = new XMLHttpRequest();
        request.open("POST", this.server, true);
        request.setRequestHeader("Content-Type", "application/json");
        request.setRequestHeader("Content-Length", body.length);
        request.setRequestHeader("Connection", "close");

        request.onreadystatechange = function() {
            if (request.readyState == 4) {
                response = JSON.parse(request.responseText);
                callback(response['id'], response['result'], response['error']);
            }
        }

        request.send(body);

    },

}
