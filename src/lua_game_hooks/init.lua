-- init.lua
-- This is the main entry point for our Lua hooks.
-- It should be required from Balatro's main.lua.

-- Setup logging to ai_debug.txt
local log_file_path = "./ai_debug.txt" -- Path to current directory as requested by user
local log_file = nil
local original_print = print

-- Attempt to open log file in append mode. If it fails, we'll fall back to original print.
local success, err = pcall(function()
    log_file = io.open(log_file_path, "a") -- "a" for append mode, using native Lua io.open
end)

if success and log_file then
    _G.print = function(...)
        local args = {...}
        local output_parts = {}
        for i, v in ipairs(args) do
            table.insert(output_parts, tostring(v))
        end
        local output = table.concat(output_parts, "\t") .. "\n" -- Use tab as separator and add newline
        log_file:write(output)
        log_file:flush() -- Ensure data is written immediately
        original_print(...) -- Also print to console if enabled
    end
    print("Redirecting print output to: " .. log_file_path)
else
    original_print("Failed to open log file at " .. log_file_path .. ": " .. tostring(err))
    original_print("Falling back to original print function.")
end


print("Balatro RAG Assistant: Initializing hooks...")

local data_extractor = require("data_extractor")
local socket_client = require("socket_client")

local M = {}

local hooks_initialized = false
local original_play_cards
local original_discard_cards
local original_update_shop

local last_game_state = nil -- To track changes in G.STATE
local last_game_round = nil -- To track changes in G.GAME.round_num
local f11_pressed_last_frame = false -- Added for "press once" F11 logic

-- Helper function to collect table keys (for printing purposes)
local function collect_keys(t)
    local keys = {}
    for k, v in pairs(t) do
        table.insert(keys, tostring(k))
    end
    return keys
end

-- Helper function to format the AI suggestion for display on the Love2D Commandline
local function format_suggestion_for_display(suggestion)
    local lines = {"--- AI Suggestion ---"}
    if suggestion and suggestion.status == "success" and suggestion.data then
        local data = suggestion.data
        table.insert(lines, "Action: " .. tostring(data.action))
        table.insert(lines, "Cards: " .. table.concat(data.card_ids, ", "))
        table.insert(lines, "Indices: " .. table.concat(data.location_indices, ", "))
        table.insert(lines, "Estimated Score: " .. tostring(data.estimated_score))
        table.insert(lines, "Win Chance: " .. tostring(data.win_chance) .. "%")
        if data.rationale then
            table.insert(lines, "Rationale: " .. tostring(data.rationale))
        end
    elseif suggestion and suggestion.status == "error" then
        table.insert(lines, "Error: " .. tostring(suggestion.message))
    else
        table.insert(lines, "Unknown suggestion format or no suggestion received.")
    end
    table.insert(lines, "---------------------")
    return table.concat(lines, "")
end

-- This function will be called from a game loop update or specific event triggers.
function M.on_game_state_change()
    print("Game state change detected, attempting to extract and send data to Python server...")

    -- 1. Extract the current game state
    local game_state = data_extractor.extract_in_round_state()
    if not game_state then
        print("Failed to extract game state.")
        return
    end

    -- 2. Send the game state to the Python server and wait for response
    local ok, response_or_err = socket_client.send_gamestate(game_state)
    if not ok then
        print("Failed to send game state (TCP): ", response_or_err)
    else
        -- Assuming response_or_err is the parsed JSON response table from socket_server.py
        if response_or_err and response_or_err.status then
            print("Game state transmission successful. Python TCP server status: " .. response_or_err.status)
            -- If the socket server returns any data (e.g., success message), print it
            if response_or_err.message then
                print("Server Message: " .. response_or_err.message)
            end
        else
            print("Game state transmission successful, but Python TCP server response was unexpected.")
        end
    end
end

function M.request_and_display_suggestion()
    print("Requesting AI suggestion from FastAPI...")
    local ok, suggestion_or_err = socket_client.request_ai_suggestion()

    if not ok then
        print("Failed to get AI suggestion (HTTP): ", suggestion_or_err)
        -- Display error to user via Love2D Commandline or similar
        print(format_suggestion_for_display({status = "error", message = suggestion_or_err}))
    else
        print("AI suggestion received.")
        -- Display the suggestion neatly
        print(format_suggestion_for_display(suggestion_or_err))
    end
end


-- Function to initialize hooks once G is available
local function initialize_hooks()
    if _G.G and _G.G.FUNCS and _G.G.update_shop then
        print("Balatro RAG Assistant: G object and target functions found, initializing hooks...")

        -- Store original game functions
        original_play_cards = _G.G.FUNCS.play_cards_from_highlighted
        original_discard_cards = _G.G.FUNCS.discard_cards_from_highlighted
        original_update_shop = _G.G.update_shop -- Correctly targeting the method on the instance G

        -- Wrapper for playing cards
        _G.G.FUNCS.play_cards_from_highlighted = function(e)
            print("Hook: play_cards_from_highlighted called")
            original_play_cards(e)
            M.on_game_state_change()
        end

        -- Wrapper for discarding cards
        _G.G.FUNCS.discard_cards_from_highlighted = function(e, hook)
            print("Hook: discard_cards_from_highlighted called")
            original_discard_cards(e, hook)
            M.on_game_state_change()
        end

        -- Wrapper for G:update_shop. This will be called whenever the shop state is updated.
        -- We'll use this to detect entry into the shop.
        function _G.G:update_shop(dt) -- Correctly defining method on the instance G
            -- Call the original update_shop function
            original_update_shop(self, dt) -- Pass self explicitly for methods

            -- Check if we just entered the shop state (G.STATE would be G.STATES.SHOP)
            -- This ensures we only trigger on_game_state_change once per entry into the shop,
            -- rather than every frame while in the shop.
            if _G.G.STATE and _G.G.STATES and last_game_state ~= _G.G.STATES.SHOP and _G.G.STATE == _G.G.STATES.SHOP then
                print("Hook: Entered shop state.")
                M.on_game_state_change()
            end
        end

        hooks_initialized = true
        print("Balatro RAG Assistant: Hooks initialized successfully.")
    end
end


-- Generic monitor for G.STATE and round changes
local original_love_update = love.update
function love.update(dt)
    -- Attempt to initialize hooks if not already done
    if not hooks_initialized then
        initialize_hooks()
    end

    -- Only proceed with monitoring if hooks are initialized (meaning G is available)
    if hooks_initialized and _G.G then
        -- Only trigger on_game_state_change if G.STATE has changed
        if _G.G.STATE and last_game_state ~= _G.G.STATE then
            print("Hook: G.STATE changed from " .. tostring(last_game_state) .. " to " .. tostring(_G.G.STATE))
            M.on_game_state_change()
            last_game_state = _G.G.STATE
        end

        -- Monitor round changes
        if _G.G.GAME and _G.G.GAME.round_num and last_game_round ~= _G.G.GAME.round_num then
            print("Hook: Round changed from " .. tostring(last_game_round) .. " to " .. tostring(_G.G.GAME.round_num))
            M.on_game_state_change()
            last_game_round = _G.G.GAME.round_num
        end
    end

    -- Original F10 trigger for testing purposes (can be removed later)
    if love.keyboard.isDown('f10') then
        M.on_game_state_change()
    end

    local f11_pressed_this_frame = love.keyboard.isDown('f11')
    if f11_pressed_this_frame and not f11_pressed_last_frame then
        M.request_and_display_suggestion()
    end
    f11_pressed_last_frame = f11_pressed_this_frame

    original_love_update(dt)
end


return M