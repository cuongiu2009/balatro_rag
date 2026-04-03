local M = {}


-- Helper function to serialize card objects into their string identifiers
local function serialize_cards(card_table)
    local serialized_cards = {}
    if type(card_table) == 'table' then
        for _, card in ipairs(card_table) do
            -- Assuming card objects have a '_name' or 'id' attribute for identification
            -- Adjust this based on actual Balatro card object structure if needed
            if type(card) == 'table' and card._name then
                table.insert(serialized_cards, card._name)
            elseif type(card) == 'table' and card.id then -- Fallback if _name isn't present
                table.insert(serialized_cards, card.id)
            else
                -- If it's not a table or doesn't have _name/id, just convert to string
                table.insert(serialized_cards, tostring(card))
            end
        end
    end
    return serialized_cards
end

-- Helper function to serialize joker objects into simpler tables
local function serialize_jokers(joker_table)
    local serialized_jokers = {}
    if type(joker_table) == 'table' then
        for _, joker in ipairs(joker_table) do
            if type(joker) == 'table' then
                local serialized_joker = {
                    name = joker.name or "Unknown Joker",
                    value = joker.value, -- Assuming 'value' is directly accessible
                    effect = joker.effect or "No Effect" -- Assuming 'effect' is directly accessible
                }
                -- Only include value if it exists
                if serialized_joker.value == nil then serialized_joker.value = nil end 
                table.insert(serialized_jokers, serialized_joker)
            end
        end
    end
    return serialized_jokers
end

-- Helper function to serialize consumable objects into their string identifiers
local function serialize_consumeables(consumeables_table)
    local serialized_consumeables = {}
    if type(consumeables_table) == 'table' then
        for _, consumable in ipairs(consumeables_table) do
            -- Assuming consumable objects have a '_name' or 'name' attribute
            if type(consumable) == 'table' and consumable._name then
                table.insert(serialized_consumeables, consumable._name)
            elseif type(consumable) == 'table' and consumable.name then -- Fallback
                table.insert(serialized_consumeables, consumable.name)
            else
                table.insert(serialized_consumeables, tostring(consumable))
            end
        end
    end
    return serialized_consumeables
end

-- This function extracts game state relevant during a round.
-- It assumes the global 'G' table is available and populated by the game.
function M.extract_in_round_state()
    local debug_path_log = {} -- New: To log path lookup steps
    
    -- Using pcall to safely access potentially nil fields in the G table
    local function safe_get_with_log(path)
        local value = _G
        local current_path_str = ""
        for i, key in ipairs(path) do
            current_path_str = current_path_str .. (i > 1 and "." or "") .. tostring(key)
            if type(value) == 'table' and value[key] then
                -- Log the value if it's not a table (to avoid circular refs in log)
                if type(value[key]) ~= 'table' then
                    table.insert(debug_path_log, current_path_str .. ": EXISTS (type: " .. type(value[key]) .. ", value: " .. tostring(value[key]) .. ")")
                else
                    table.insert(debug_path_log, current_path_str .. ": EXISTS (type: " .. type(value[key]) .. ")")
                end
                value = value[key]
            else
                table.insert(debug_path_log, current_path_str .. ": DOES NOT EXIST or NOT TABLE at " .. tostring(key) .. " in " .. type(value))
                return nil
            end
        end
        return value
    end

    local game_state = {
        player_hand = serialize_cards(safe_get_with_log({'G', 'hand'})),
        active_jokers = serialize_jokers(safe_get_with_log({'G', 'jokers'})),
        consumeables = serialize_consumeables(safe_get_with_log({'G', 'consumeables'})), -- Now serialized
        dollars = safe_get_with_log({'G', 'GAME', 'dollars'}) or 0,
        hands_remaining = safe_get_with_log({'G', 'GAME', 'current_round', 'hands_left'}) or 0,
        discards_remaining = safe_get_with_log({'G', 'GAME', 'current_round', 'discards_left'}) or 0,
        current_blind_name = (safe_get_with_log({'G', 'GAME', 'blind'}) and safe_get_with_log({'G', 'GAME', 'blind', 'name'})) or "Unknown Blind"
    }



    game_state.debug_path_log = debug_path_log -- Add the path log to game_state

    return game_state
end


-- In the future, other functions could be added for different game phases.
-- function M.extract_shop_state() ... end

return M
