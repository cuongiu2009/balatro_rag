local socket = require("socket")
local http = require("socket.http") -- Added for HTTP requests
local json = require("json") 
local ltn12 = require("ltn12")

local M = {}

-- Helper function to pack a number as a 4-byte little-endian unsigned integer
local function pack_u32_le(value)
    local byte1 = value % 256
    local byte2 = math.floor(value / 256) % 256
    local byte3 = math.floor(value / 65536) % 256
    local byte4 = math.floor(value / 16777216) % 256
    return string.char(byte1, byte2, byte3, byte4)
end

M.host = "127.0.0.1"
M.port = 5000
M.fastapi_host = "127.0.0.1"
M.fastapi_port = 8000

function M.send_gamestate(game_state)
    print("Lua: Attempting to send game state via TCP...")
    local tcp = socket.tcp()
    
    tcp:settimeout(5) -- Set a 5-second timeout for all subsequent TCP operations

    local ok, err = tcp:connect(M.host, M.port)
    if not ok then
        print("Lua Error: Failed to connect to Python TCP server at " .. M.host .. ":" .. M.port .. " - " .. tostring(err))
        tcp:close()
        return false, err
    end
    print("Lua: Successfully connected to Python TCP server.")

    local json_data, json_err = json.encode(game_state)
    if not json_data then
        print("Lua Error: Failed to encode game state to JSON: ", json_err)
        tcp:close()
        return false, json_err
    end
    print("Lua: Game state encoded to JSON. Length: " .. tostring(#json_data))

    local message_length = #json_data
    -- Pack the message_length into a 4-byte little-endian unsigned integer
    local length_prefix_bytes = pack_u32_le(message_length) 
    
    -- Concatenate the binary length prefix with the JSON data
    local full_message_to_send = length_prefix_bytes .. json_data

    local sent_data_bytes, send_data_err = tcp:send(full_message_to_send)
    if not sent_data_bytes then
        print("Lua Error: Failed to send data over TCP: ", send_data_err)
        tcp:close()
        return false, send_data_err
    end
    print("Lua: Data sent over TCP. Sent bytes: " .. tostring(sent_data_bytes))
    
    print("Lua: Waiting for response from Python TCP server...")
    
    -- Read the 4-byte length prefix for the response
    local response_length_prefix, len_recv_err = tcp:receive(4) -- Read exactly 4 bytes
    if not response_length_prefix then
        print("Lua Error: Failed to receive response length prefix from Python TCP server: ", len_recv_err)
        tcp:close()
        return false, len_recv_err
    end
    
    -- Unpack the length (assuming little-endian unsigned int, same as Python's struct.pack('<I', ...))
    -- Note: Lua's string.byte returns ASCII value (0-255)
    local response_length = (string.byte(response_length_prefix, 1)        ) +
                            (string.byte(response_length_prefix, 2) * 256     ) +
                            (string.byte(response_length_prefix, 3) * 65536   ) +
                            (string.byte(response_length_prefix, 4) * 16777216)
                            
    print("Lua: Received response length: " .. tostring(response_length) .. " bytes.")

    -- Read the exact number of bytes for the response data
    local received_data, recv_err = tcp:receive(response_length)
    if not received_data then
        print("Lua Error: Failed to receive response data from Python TCP server: ", recv_err)
        tcp:close()
        return false, recv_err
    end
    print("Lua: Received response from Python TCP server. Data: " .. received_data)

    local response, json_parse_err = json.decode(received_data)
    if not response then
        print("Lua Error: Failed to parse JSON response from Python TCP server: ", json_parse_err .. " - Raw: " .. received_data)
        tcp:close()
        return false, "Invalid JSON response from TCP: " .. (json_parse_err or "unknown error")
    end
    print("Lua: Successfully parsed JSON response from Python TCP server.")

    tcp:close()
    
    return true, response
end

function M.request_ai_suggestion()
    print("Requesting AI suggestion from FastAPI...")
    local url = "http://" .. M.fastapi_host .. ":" .. M.fastapi_port .. "/suggestion"

    local payload = {} 
    local json_data = json.encode(payload)

    local response_chunks = {} 

    local res, code, response_headers, status = http.request{
        method = "POST",
        url = url,
        headers = {
            ["Content-Type"] = "application/json",
            ["Content-Length"] = tostring(#json_data)
        },
        source = ltn12.source.string(json_data),
        sink = ltn12.sink.table(response_chunks), -- 
        timeout = 10 -- 
    }

    -- Trong LuaSocket, nếu dùng sink, 'res' trả về 1 là thành công 
    if not res or code ~= 200 then
        local err_msg = status or ("Code " .. tostring(code))
        print("Failed to make HTTP request: ", err_msg)
        return false, err_msg
    end

    -- Hợp nhất các mảnh dữ liệu từ sink table 
    local response_body = table.concat(response_chunks)
    print("FastAPI Response Body: " .. response_body)

    local suggestion, json_err = json.decode(response_body)
    if not suggestion then
        return false, "Invalid JSON: " .. (json_err or "unknown")
    end

    return true, suggestion
end

return M
