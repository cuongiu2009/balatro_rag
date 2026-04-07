-- File: src/lua_game_hooks/extract_joker_data.lua

-- IMPORTANT: Script này chỉ dành cho *mục đích thử nghiệm và trích xuất dữ liệu*.
-- Nó nên được load/dofile tạm thời để gỡ lỗi.

-- Một bộ mã hóa JSON đơn giản, tự chứa.
-- Không xử lý mọi trường hợp cạnh của JSON (ví dụ: các ký tự unicode phức tạp),
-- nhưng đủ cho các kiểu dữ liệu cơ bản.
local function simple_json_encode(val, indent_str, current_indent_level, tables_seen)
    indent_str = indent_str or '  '
    current_indent_level = current_indent_level or 0
    tables_seen = tables_seen or {}

    local result_parts = {}
    local val_type = type(val)

    if val_type == 'table' then
        if tables_seen[val] then
            return '"[...circular reference...]"'
        end
        tables_seen[val] = true

        local is_array = true
        for k in pairs(val) do
            if type(k) ~= 'number' or k < 1 or math.floor(k) ~= k then is_array = false; break end
        end

        local current_indent = string.rep(indent_str, current_indent_level)
        local next_indent = string.rep(indent_str, current_indent_level + 1)

        if is_array then
            table.insert(result_parts, '[')
            for i, v in ipairs(val) do
                table.insert(result_parts, '' .. next_indent .. simple_json_encode(v, indent_str, current_indent_level + 1, tables_seen))
                table.insert(result_parts, ',')
            end
            if #val > 0 then table.remove(result_parts) end -- remove last comma
            table.insert(result_parts, '' .. current_indent .. ']')
        else
            table.insert(result_parts, '{')
            local first_field = true
            for k, v in pairs(val) do
                -- Bỏ qua các giá trị nil, function, userdata để tránh lỗi JSON
                if type(v) ~= 'nil' and type(v) ~= 'function' and type(v) ~= 'userdata' then
                    if not first_field then table.insert(result_parts, ',') end
                    table.insert(result_parts, '' .. next_indent .. simple_json_encode(k, indent_str, 0, tables_seen)) -- key should not be indented further
                    table.insert(result_parts, ': ')
                    table.insert(result_parts, simple_json_encode(v, indent_str, current_indent_level + 1, tables_seen))
                    first_field = false
                end
            end
            if not first_field then table.insert(result_parts, '' .. current_indent) end
            table.insert(result_parts, '}')
        end
        tables_seen[val] = nil -- remove from seen tables
        return table.concat(result_parts)

    elseif val_type == 'number' or val_type == 'boolean' then
        return tostring(val)
    elseif val_type == 'string' then
        -- Escape special characters for JSON string
        local escaped_string = string.gsub(val, '[%"]', {['"'] = '"', [''] = '', [''] = '', [''] = '', ['	'] = '	'})
        return '"' .. escaped_string .. '"'
    elseif val_type == 'nil' then
        return 'null'
    else -- function, userdata, thread (should be caught by the if type(v) checks above, but as a fallback)
        return 'null'
    end
end


local json_output_filename = "joker_data_dump.json"
-- Lưu file vào thư mục lưu của Love2D (ví dụ: C:\Users\<User>\AppData\Roaming\LOVE\Balatro)
local log_file_path = "E:/BalatroTest/balatro_mod/" .. json_output_filename

local extracted_jokers = {}

-- Giả định _G.G.P_CENTRE chứa bảng các định nghĩa Joker hoặc tham chiếu đến chúng.
-- (Lưu ý: "P_CENTRE" không phải là một global tiêu chuẩn trong Balatro, nó có thể là của mod hoặc nội bộ)
if _G.G and _G.G.P_CENTRE and type(_G.G.P_CENTRE) == 'table' then
    for key, item in pairs(_G.G.P_CENTRE) do
        -- Đây là phỏng đoán về cấu trúc Joker.
        -- Joker thường có name và effect/description.
        if type(item) == 'table' then
            local name = item.name or item._name
            local description = item.description or (item.ability and item.ability.effect) or item.effect or item.text -- Thử nhiều trường cho description

            -- Nếu tìm thấy name và description (hoặc effect), giả định đây là một Joker hợp lệ.
            if name and (description ~= nil and description ~= "") then
                local joker_info = {
                    key = tostring(key), -- Sử dụng key của bảng làm định danh
                    name = name,
                    description = description
                    -- Bạn có thể thêm các thuộc tính khác ở đây nếu cần và nếu chúng có sẵn
                    -- Ví dụ: id = item.id, rarity = item.rarity, value = item.value
                }
                table.insert(extracted_jokers, joker_info)
            end
        end
    end
end

-- Ghi dữ liệu đã trích xuất vào file JSON
local file = io.open(log_file_path, "w")
if file then
    local json_string = simple_json_encode(extracted_jokers, '  ', 0, {})
    file:write(json_string)
    file:close()
    print("DEBUG (Lua Script): Dữ liệu Joker đã được trích xuất thành công vào: " .. log_file_path)
else
    print("ERROR (Lua Script): Không thể mở file " .. log_file_path .. " để ghi.")
end

-- Sau khi script này chạy, file joker_data_dump.json sẽ được tạo trong thư mục lưu của Love2D.
-- Bạn có thể tìm thấy thư mục này bằng cách chạy Love2D, sau đó trong console gõ:
-- love.filesystem.getSaveDirectory()
-- Thông thường nó ở đâu đó như: C:\Users\<User>\AppData\Roaming\LOVE\<Game_Name>
