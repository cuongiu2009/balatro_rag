local M = {}

-- Add a recursive table printer function
M.print_table_recursive = function(t, indent, visited, max_depth, current_depth)
    indent = indent or 0
    visited = visited or {}
    max_depth = max_depth or 3 -- Limit recursion depth
    current_depth = current_depth or 0

    if current_depth > max_depth then
        print(string.rep("  ", indent) .. "{... (max depth reached) ...}")
        return
    end

    if type(t) ~= "table" then
        print(string.rep("  ", indent) .. tostring(t))
        return
    end

    if visited[t] then
        print(string.rep("  ", indent) .. "{... (circular reference) ...}")
        return
    end
    visited[t] = t -- Mark as visited, store the table itself as the value

    print(string.rep("  ", indent) .. "{")
    for k, v in pairs(t) do
        -- Limit output length for values to avoid super long lines
        local val_str = tostring(v)
        if #val_str > 100 then val_str = string.sub(val_str, 1, 100) .. "..." end

        if type(v) == "table" and not visited[v] then
            print(string.rep("  ", indent + 1) .. tostring(k) .. " = ")
            M.print_table_recursive(v, indent + 2, visited, max_depth, current_depth + 1)
        else
            print(string.rep("  ", indent + 1) .. tostring(k) .. " = " .. val_str)
        end
    end
    print(string.rep("  ", indent) .. "}")
end


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

    local hand_data_container = safe_get_with_log({'G', 'hand'})
    print("DEBUG Lua: Raw G.hand data container:", hand_data_container == nil and "nil" or type(hand_data_container) .. " (count: " .. #hand_data_container .. ")")
    local jokers_data_container = safe_get_with_log({'G', 'jokers'})
    print("DEBUG Lua: Raw G.jokers data container:", jokers_data_container == nil and "nil" or type(jokers_data_container) .. " (count: " .. #jokers_data_container .. ")")
    local consumeables_data_container = safe_get_with_log({'G', 'consumeables', 'cards'})
    print("DEBUG Lua: Raw G.consumeables data container:", consumeables_data_container == nil and "nil" or type(consumeables_data_container) .. " (count: " .. #consumeables_data_container .. ")")

    local game_state = {
        player_hand = {}, -- Initialize as empty table, will be populated below
        active_jokers = {}, -- Initialize as empty table, will be populated below
        consumeables = serialize_consumeables(consumeables_data_container),
        dollars = safe_get_with_log({'G', 'GAME', 'dollars'}) or 0,
        hands_remaining = safe_get_with_log({'G', 'GAME', 'current_round', 'hands_left'}) or 0,
        discards_remaining = safe_get_with_log({'G', 'GAME', 'current_round', 'discards_left'}) or 0,
        current_blind_name = (safe_get_with_log({'G', 'GAME', 'blind'}) and safe_get_with_log({'G', 'GAME', 'blind', 'name'})) or "Unknown Blind"
    }

    -- Trích xuất bài trên tay (phải dùng G.hand.cards)
    local G_hand_cards = safe_get_with_log({'G', 'hand', 'cards'})
    if G_hand_cards and type(G_hand_cards) == 'table' then
        for i, card in ipairs(G_hand_cards) do
            if type(card) == 'table' then -- Ensure it's a card object
                local card_data = {
                    id = card.id or "UnknownID",
                    name = (card.get_full_name and card:get_full_name()) or (card._name and card._name) or "Unknown Card",
                    rank = (card.base and card.base.value) or "Unknown Rank",
                    suit = (card.base and card.base.suit) or "Unknown Suit",
                    enhancement = card.enhancement or nil, -- Add enhancement if available
                    edition = card.edition or nil -- Add edition if available
                }
                table.insert(game_state.player_hand, card_data)
            end
        end
    end

    -- Tương tự với Joker
    local G_jokers_cards = safe_get_with_log({'G', 'jokers', 'cards'})
    if G_jokers_cards and type(G_jokers_cards) == 'table' then
        for i, joker in ipairs(G_jokers_cards) do -- 'joker' here is a joker object
            if type(joker) == 'table' then
                local joker_data = {
                    id = joker.id or joker.key or "UnknownID", -- Try joker.id, then joker.key for ID
                    name = (joker.ability and joker.ability.name) or (joker._name and joker._name) or "Unknown Joker",
                    effect = joker.effect or (joker.ability and joker.ability.effect) or "No Effect", -- Try joker.effect, then joker.ability.effect for effect
                    rarity = (joker.ability and joker.ability.rarity) or nil
                }
                table.insert(game_state.active_jokers, joker_data)
            end
        end
    end

    -- Add this debug print after game_state is populated, or when G.STATE indicates active play
    print("DEBUG Lua: Full G table dump:")
    M.print_table_recursive(_G.G, 0, nil, 3, 0) -- Dump G up to depth 3


    game_state.debug_path_log = debug_path_log -- Add the path log to game_state

    return game_state
end


-- In the future, other functions could be added for different game phases.
-- function M.extract_shop_state() ... end

return M
