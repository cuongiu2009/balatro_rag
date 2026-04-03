-- test_connection.lua
-- Run this with `lua test_connection.lua`
-- Make sure luasocket and a json library are installed for your Lua environment.

local socket = require("socket")
local json = require("json") -- Assumes a json.lua library is in the path

local function test_luasocket_connection()
    print("Testing Lua->Python connection...")

    local test_payload = {
        player_hand = {"H_2", "S_8"},
        active_jokers = {},
        discard_pile = {},
        played_cards_history = {},
        current_score = 50,
        current_blind_info = {name = "Small Blind", chips_required = 300, reward = 10},
        active_global_modifiers_challenges = {},
        shop_contents = {},
        current_stakes = 1
    }
    
    local json_data, json_err = json.encode(test_payload)
    if not json_data then
        print("Error encoding JSON:", json_err)
        return
    end

    local tcp = socket.tcp()
    local ok, err = tcp:connect("127.0.0.1", 5000)

    if not ok then
        print("Failed to connect to FastAPI server:", err)
        return
    end

    print("Connected to FastAPI server.")

    -- The FastAPI server expects a POST request with a JSON body.
    -- A raw socket send needs to be formatted as an HTTP POST request.
    local request_body = json_data
    local request_headers = {
        "Host: 127.0.0.1:5000",
        "Content-Type: application/json",
        "Content-Length: " .. #request_body,
    }
    
    local http_request = "POST /gamestate HTTP/1.1
" ..
                       table.concat(request_headers, "
") ..
                       "

" ..
                       request_body

    print("Sending HTTP POST request...")
    local sent, send_err = tcp:send(http_request)

    if not sent then
        print("Failed to send data:", send_err)
        tcp:close()
        return
    end

    print("Data sent successfully.")
    
    -- Wait for a response
    local response, rec_err = tcp:receive('*a')
    if rec_err then
        print("Error receiving response:", rec_err)
    else
        print("Received response:
", response)
    end
    
    tcp:close()
end

test_luasocket_connection()
