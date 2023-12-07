import json

import quart
import quart_cors
import httpx
import requests


from quart import request

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}

@app.post("/todos/<string:username>")
async def add_todo(username):
    request = await quart.request.get_json(force=True)
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(request["todo"])
    return quart.Response(response='OK', status=200)

@app.get("/todos/<string:username>")
async def get_todos(username):
    return quart.Response(response=json.dumps(_TODOS.get(username, [])), status=200)

@app.delete("/todos/<string:username>")
async def delete_todo(username):
    request = await quart.request.get_json(force=True)
    todo_idx = request["todo_idx"]
    # fail silently, it's a simple plugin
    if 0 <= todo_idx < len(_TODOS[username]):
        _TODOS[username].pop(todo_idx)
    return quart.Response(response='OK', status=200)

@app.get("/external_api")
async def external_api_call():
    host = request.headers['Host']
    url = "https://services.odata.org/TripPinRESTierService/People"

    # Make a GET request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse JSON response
        data = response.json()
        print(data)
    else:
        print("Failed to retrieve data:", response.status_code)
        
    # async with httpx.AsyncClient() as client:
    #     resp = await client.get(url)
    #     print(resp)
    #     data = resp.json()
    
    #return quart.Response(data, mimetype="text/text")
    return quart.Response(response=json.dumps(data), status=response.status_code)

    # #url = "https://d2dd45bb-32b7-45c7-b7d5-1328f3781129.abap-web.us10.hana.ondemand.com/sap/opu/odata/sap/ZAPI_ODV2_C_TRAVEL_M_257/?sap-client=100"
    # return quart.Response(response=json.dumps(data), status=resp.status_code)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5012)

if __name__ == "__main__":
    main()
