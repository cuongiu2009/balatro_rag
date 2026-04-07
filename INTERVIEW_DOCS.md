# Trợ lý Chiến lược AI Balatro (dựa trên RAG) - Tài liệu Phỏng vấn

Tài liệu này cung cấp tổng quan kỹ thuật chi tiết về dự án Trợ lý Chiến lược AI Balatro, được thiết kế làm tài liệu học tập cho các buổi phỏng vấn kỹ thuật. Nó giải thích kiến trúc của dự án, luồng dữ liệu, các cơ chế chính như Tạo sinh có Trích xuất Nâng cao (RAG), và những chi tiết tinh tế của quá trình chuyển đổi dữ liệu giữa các thành phần hệ thống khác nhau.

## 1. Tổng quan dự án

Trợ lý Chiến lược AI Balatro là một hệ thống AI và sửa đổi trò chơi sáng tạo tích hợp trực tiếp với trò chơi Balatro (được xây dựng trên công cụ Love2D). Chức năng chính của nó là cung cấp cập nhật trạng thái trò chơi theo thời gian thực và các gợi ý chiến lược chơi game cho người chơi. Điều này đạt được thông qua:

*   **Runtime Hooking**: Tiêm các tập lệnh Lua vào trò chơi Balatro đang chạy để trích xuất thông tin trạng thái trò chơi toàn diện (ví dụ: bài trên tay người chơi, Joker đang hoạt động, thành phần bộ bài, bài bỏ, điểm số, nội dung cửa hàng).
*   **Giao tiếp giữa các tiến trình**: Truyền dữ liệu trò chơi thời gian thực này đến một bộ điều phối Python bên ngoài.
*   **Phân tích AI (RAG)**: Sử dụng một Mô hình Ngôn ngữ Lớn (LLM) cục bộ thông qua LM Studio, được tăng cường bởi hệ thống RAG (ChromaDB), để xử lý trạng thái trò chơi và tạo ra lời khuyên chiến lược tối ưu.
*   **Hiển thị trong trò chơi**: Trình bày các gợi ý và cập nhật trạng thái trò chơi của AI trực tiếp trong giao diện dòng lệnh Love2D, đảm bảo trải nghiệm người dùng tích hợp.

Dự án thể hiện các kỹ năng nâng cao trong **Tích hợp Hệ thống**, **Kỹ thuật AI**, **Hệ thống Độ trễ Thấp**, và **Kỹ thuật Dữ liệu**.

## 2. Kiến trúc chi tiết

Hệ thống bao gồm một số thành phần liên kết với nhau:

```
+-------------------+        +---------------------------+        +---------------------+        +-----------------+
| Trò chơi Balatro  |        | Bộ điều phối Python       |        | LM Studio (LLM)     |        | ChromaDB        |
| (Công cụ Love2D)  |        | (Ứng dụng FastAPI)        |        | (Mô hình AI cục bộ) |        | (Cơ sở tri thức)|
+-------------------+        +---------------------------+        +---------------------+        +-----------------+
        |                            ^             ^                        ^                      ^
        | (1) Lua Runtime Hooks      |             |                        |                      |
        |    - init.lua              |             | (5) Gợi ý AI           |                      |
        |    - data_extractor.lua    |             |    (JSON)              | (6) Truy vấn RAG      | (7) Dữ liệu
        |    - socket_client.lua     |             |                        |                      |     ngữ cảnh
        V                            |             |                        |                      |
+-------------------+        +---------------------------+        +---------------------+        +-----------------+
| Trích xuất        |<-------| (4) Hiển thị gợi ý      |          |  api_client/        |        | rag_model/          |
| Trạng thái Game   |        |    trên dòng lệnh Love2D  |        |  lm_studio_client.py|<-----> |   chromadb_client.py|
| (JSON)            |        |                            |       |                     |        |   data_processor.py |
+-------------------+        +---------------------------+        |    (localhost:1234) |        |   knowledge_base_builder.py|
        | (2) Socket TCP             |             |        +---------------------+        |   rag_processor.py    |
        |    (localhost:5000)        |             |                                       +-----------------+
        V                            |             |
+-------------------+        +---------------------------+
| src/common/       |        | communication/            |
|   game_state_schema.lua    |   socket_server.py        |
|   game_state_schema.py     |<--------------------------+
+-------------------+        | rag_model/                |
                             |   rag_processor.py (Logic RAG) |
                             +---------------------------+
```

### Các thành phần:

1.  **Trò chơi Balatro (Công cụ Love2D)**:
    *   Môi trường trò chơi cốt lõi.
    *   **`src/lua_game_hooks/init.lua`**: Điểm vào cho tất cả các sửa đổi Lua. Nó được tiêm vào `main.lua` của Balatro và chịu trách nhiệm tải các mô-đun Lua khác cũng như thiết lập các hook toàn cục.
    *   **`src/lua_game_hooks/data_extractor.lua`**: Chứa logic để truy cập và trích xuất trạng thái trò chơi thời gian thực từ các bảng Lua toàn cục của Balatro (bảng `G`). Nó giám sát các sự kiện cụ thể trong trò chơi (ví dụ: rút bài, bỏ bài, mở cửa hàng) để kích hoạt quá trình trích xuất dữ liệu.
    *   **`src/lua_game_hooks/socket_client.lua`**: Một client Lua `Luasocket` chịu trách nhiệm tuần tự hóa trạng thái trò chơi đã trích xuất thành định dạng JSON tiêu chuẩn và gửi nó qua socket TCP đến Bộ điều phối Python.
    *   **Dòng lệnh Love2D**: Giao diện trong trò chơi được sử dụng để hiển thị các cập nhật trạng thái trò chơi đã trích xuất và các gợi ý chiến lược từ AI.

2.  **Bộ điều phối Python (Ứng dụng FastAPI)**:
    *   Một ứng dụng FastAPI hoạt động như một trung tâm điều khiển, quản lý giao tiếp, xử lý RAG và tương tác AI.
    *   **`src/python_orchestrator/main.py`**: Điểm vào cho ứng dụng FastAPI, định nghĩa các điểm cuối API để giao tiếp với client Lua.
    *   **`src/python_orchestrator/communication/socket_server.py`**: Xử lý các kết nối socket TCP đến từ client Lua, nhận trạng thái trò chơi JSON thô và giải tuần tự hóa nó.
    *   **`src/python_orchestrator/rag_model/`**:
        *   **`chromadb_client.py`**: Quản lý kết nối và các hoạt động với ChromaDB, bao gồm lưu trữ và truy xuất các nhúng vector.
        *   **`data_processor.py`**: Một tập lệnh tiện ích được sử dụng ngoại tuyến để xử lý dữ liệu trò chơi Balatro thô (ví dụ: mô tả thẻ, hiệu ứng Joker) thành định dạng có cấu trúc phù hợp cho cơ sở tri thức.
        *   **`knowledge_base_builder.py`**: Một tập lệnh tiện ích chịu trách nhiệm vector hóa dữ liệu trò chơi đã xử lý và điền vào cơ sở tri thức ChromaDB.
        *   **`rag_processor.py`**: Logic RAG cốt lõi. Nó lấy trạng thái trò chơi hiện tại, truy xuất ngữ cảnh liên quan từ ChromaDB và tạo ra một lời nhắc tăng cường cho LLM.
    *   **`src/python_orchestrator/api_client/lm_studio_client.py`**: Một client để tương tác với API LM Studio cục bộ (`localhost:1234`). Nó gửi các lời nhắc tăng cường đến LLM và xử lý các phản hồi thô của nó.

3.  **LM Studio (Mô hình AI cục bộ)**:
    *   Một máy chủ suy luận cục bộ chạy một LLM đã được tinh chỉnh (ví dụ: một mô hình chiến lược Balatro cụ thể).
    *   Nhận lời nhắc từ Bộ điều phối Python và tạo ra các gợi ý chiến lược.

4.  **ChromaDB (Cơ sở tri thức)**:
    *   Một cơ sở dữ liệu vector được sử dụng để lưu trữ thông tin vector hóa về cơ chế trò chơi, thẻ bài, Joker và quy tắc tính điểm của Balatro.
    *   Đóng vai trò là nguồn tri thức bên ngoài cho hệ thống RAG, cung cấp ngữ cảnh cho LLM.

### Thành phần chia sẻ:

*   **`src/common/`**: Chứa các cấu trúc dữ liệu và lược đồ chia sẻ.
    *   **`game_state_schema.lua` / `game_state_schema.py`**: Định nghĩa lược đồ JSON tiêu chuẩn cho trạng thái trò chơi, đảm bảo biểu diễn dữ liệu nhất quán giữa Lua và Python.

## 3. Luồng dữ liệu: Hành trình từ đầu đến cuối

Hệ thống hoạt động trong một vòng lặp liên tục, được kích hoạt bởi các sự kiện trong trò chơi:

1.  **Kích hoạt sự kiện**: Một sự kiện trong trò chơi xảy ra (ví dụ: người chơi rút bài, chơi một ván bài, vào cửa hàng).
2.  **Trích xuất dữ liệu Lua**: `data_extractor.lua` (được hook vào runtime của Balatro) phát hiện sự kiện và truy cập các bảng trò chơi toàn cục (`G`) để thu thập thông tin trạng thái trò chơi toàn diện, thời gian thực.
3.  **Tuần tự hóa Lua**: `socket_client.lua` tuần tự hóa dữ liệu Lua thô này thành một chuỗi JSON tiêu chuẩn, tuân thủ lược đồ được định nghĩa trong `src/common/game_state_schema.lua`.
4.  **Truyền từ Lua sang Python**: Chuỗi JSON được gửi qua socket TCP từ `socket_client.lua` đến thành phần `socket_server.py` trong Bộ điều phối Python (`localhost:5000`).
5.  **Giải tuần tự hóa Python**: `socket_server.py` nhận chuỗi JSON và giải tuần tự hóa nó thành một đối tượng Python (ví dụ: một từ điển hoặc mô hình Pydantic), xác thực nó dựa trên `src/common/game_state_schema.py`.
6.  **Truy xuất ngữ cảnh RAG**: `rag_processor.py` lấy trạng thái trò chơi hiện tại. Sau đó, nó truy vấn ChromaDB (thông qua `chromadb_client.py`) để truy xuất thông tin ngữ cảnh (ví dụ: hiệu ứng chi tiết của Joker đang hoạt động, quy tắc tính điểm cho các ván bài poker cụ thể) có liên quan đến tình hình trò chơi hiện tại. Việc truy xuất này dựa trên sự tương đồng ngữ nghĩa.
7.  **Tạo lời nhắc**: `rag_processor.py` xây dựng một lời nhắc toàn diện cho LLM. Lời nhắc này bao gồm:
    *   Trạng thái trò chơi hiện tại (được trích xuất từ Lua).
    *   Thông tin ngữ cảnh đã truy xuất từ ChromaDB.
    *   Hướng dẫn rõ ràng cho LLM để tạo ra lời khuyên chiến lược ở định dạng JSON có cấu trúc cụ thể.
8.  **Suy luận LLM**: Lời nhắc tăng cường được gửi đến phiên bản LM Studio cục bộ thông qua `lm_studio_client.py` (`localhost:1234`).
9.  **Tạo gợi ý AI**: LLM xử lý lời nhắc, áp dụng kiến thức đã học (mô hình đã tinh chỉnh) và ngữ cảnh RAG được cung cấp để tạo ra các gợi ý chiến lược (ví dụ: "Chơi Flush: 5H, 6H, 7H, 8H, 9H - Điểm dự kiến: 1200 Chip, 12x Mult"). Đầu ra được định dạng nghiêm ngặt dưới dạng JSON có cấu trúc.
10. **Phân tích phản hồi Python**: `lm_studio_client.py` nhận phản hồi JSON của LLM, phân tích nó và xử lý mọi đầu ra hoặc lỗi không đúng định dạng.
11. **Định dạng & Truyền Python**: Bộ điều phối Python định dạng gợi ý (và tùy chọn, xác nhận trạng thái trò chơi đã cập nhật) thành một chuỗi hoặc một tin nhắn JSON đơn giản hóa phù hợp để hiển thị trên Dòng lệnh Love2D. Tin nhắn này sau đó được gửi trở lại client trò chơi Lua.
12. **Hiển thị Lua**: `init.lua` (hoặc một mô-đun hiển thị chuyên dụng) nhận tin nhắn và hiển thị nó gọn gàng trên Dòng lệnh Love2D, cung cấp phản hồi ngay lập tức cho người chơi.

## 4. Tìm hiểu sâu về RAG

Tạo sinh có Trích xuất Nâng cao (RAG) là một phần quan trọng của dự án này, cho phép LLM cung cấp lời khuyên chính xác và có liên quan đến ngữ cảnh mà không cần phải liên tục đào tạo lại trên dữ liệu cụ thể của trò chơi.

### Tại sao RAG?

*   **Thông tin cập nhật**: Balatro là một trò chơi sống động; các thẻ bài, Joker mới hoặc thay đổi cân bằng có thể xảy ra. RAG cho phép hệ thống truy cập các cơ chế trò chơi mới nhất được lưu trữ trong ChromaDB mà không cần đào tạo lại LLM.
*   **Giảm "ảo giác"**: LLM có thể "ảo giác" hoặc cung cấp thông tin sai lệch. Bằng cách neo các phản hồi của LLM với thông tin có thể kiểm chứng từ cơ sở tri thức chuyên dụng, RAG giảm đáng kể khả năng đưa ra lời khuyên chiến lược không chính xác.
*   **Tính đặc thù**: Balatro có các quy tắc và tương tác thẻ bài phức tạp. RAG đảm bảo LLM nhận được các chi tiết cụ thể về từng yếu tố trò chơi liên quan đến trạng thái hiện tại, dẫn đến các gợi ý chính xác hơn.
*   **Hiệu quả chi phí**: Tinh chỉnh một LLM cho mỗi bản cập nhật trò chơi là tốn kém và tốn thời gian. Cập nhật cơ sở dữ liệu vector hiệu quả hơn nhiều.

### Xây dựng cơ sở tri thức (`src/python_orchestrator/rag_model/`)

1.  **`data_processor.py`**:
    *   **Mục đích**: Xử lý dữ liệu trò chơi Balatro thô, không có cấu trúc (ví dụ: dữ liệu được trích xuất từ ​​tệp trò chơi, wiki hoặc tài liệu chính thức) thành định dạng sạch, có cấu trúc phù hợp để nhúng.
    *   **Quá trình**: Tập lệnh này có thể phân tích mô tả văn bản của Joker, thẻ Tarot, thẻ Planet, quy tắc tính điểm, debuff và thử thách. Nó trích xuất các thuộc tính chính và sắp xếp chúng.
    *   **Đầu ra**: Một tập hợp các văn bản hoặc đối tượng JSON có cấu trúc, mỗi đối tượng đại diện cho một thực thể hoặc quy tắc trò chơi riêng biệt.

2.  **`knowledge_base_builder.py`**:
    *   **Mục đích**: Lấy dữ liệu đã xử lý, chuyển đổi nó thành các nhúng vector số, và lưu trữ các nhúng này cùng với văn bản gốc của chúng (hoặc siêu dữ liệu) trong ChromaDB.
    *   **Quá trình**:
        *   **Chia/Phân đoạn văn bản**: Trước khi nhúng, văn bản đã xử lý được chia thành các "đoạn" nhỏ hơn, có ý nghĩa. Đối với dự án này, **chiến lược phân đoạn dựa trên thực thể** là tối quan trọng. Thay vì chia đoạn văn bản tùy ý, mỗi thực thể trò chơi riêng biệt (ví dụ: một Joker cụ thể, một thẻ Tarot, một cơ chế tính điểm) được coi là một đoạn độc lập. Điều này đảm bảo rằng khi một hiệu ứng của Joker được truy vấn, toàn bộ mô tả của Joker đó được truy xuất, không chỉ một câu một phần.
        *   **Nhúng**: Mỗi đoạn được đưa qua một mô hình nhúng (thường là Sentence Transformer hoặc mô hình tương tự) chuyển đổi văn bản thành một vector có chiều cao. Vector này nắm bắt ý nghĩa ngữ nghĩa của văn bản.
        *   **Lưu trữ trong ChromaDB**: Các nhúng được tạo, cùng với văn bản gốc liên quan và bất kỳ siêu dữ liệu liên quan nào (ví dụ: 'type: Joker', 'name: Joker A'), được lưu trữ trong ChromaDB.

### Cơ chế truy xuất (`src/python_orchestrator/rag_model/rag_processor.py`)

1.  **Ngữ cảnh hóa trạng thái trò chơi**: Khi một trạng thái trò chơi mới đến, `rag_processor.py` xác định các thực thể và khái niệm chính trong trạng thái đó (ví dụ: "Joker đang hoạt động: [Joker A, Joker B]", "ván bài poker: Flush", "blind hiện tại: Small Blind").
2.  **Truy vấn ChromaDB**: Các thực thể và khái niệm đã xác định này được sử dụng làm truy vấn đối với ChromaDB. `chromadb_client.py` tìm các nhúng trong cơ sở dữ liệu có ý nghĩa tương tự như các thực thể truy vấn.
3.  **Tập hợp ngữ cảnh**: Văn bản gốc (hoặc siêu dữ liệu) tương ứng với K nhúng tương tự nhất được truy xuất. Điều này tạo thành "ngữ cảnh đã truy xuất". Ví dụ: nếu "Joker A" đang hoạt động, toàn bộ mô tả và hiệu ứng của nó sẽ được kéo từ cơ sở tri thức.
4.  **Tăng cường lời nhắc**: Ngữ cảnh đã truy xuất sau đó được tích hợp liền mạch vào lời nhắc cùng với trạng thái trò chơi hiện tại và các hướng dẫn của LLM. Lời nhắc tăng cường này cung cấp cho LLM tất cả thông tin cần thiết để tạo ra một phản hồi có thông tin tốt.

## 5. Chuyển đổi dữ liệu: Lua sang LLM

Phần này trình bày chi tiết cách dữ liệu trò chơi từ Balatro được trích xuất, tiêu chuẩn hóa và chuẩn bị để LLM tiêu thụ.

### 5.1. Trích xuất trạng thái trò chơi Lua (`src/lua_game_hooks/data_extractor.lua`)

*   **Cơ chế**: Công cụ Love2D phơi bày trạng thái nội bộ của nó thông qua các bảng Lua toàn cục, đáng chú ý nhất là bảng `G`. `data_extractor.lua` tận dụng các khả năng siêu lập trình của Lua (ví dụ: bằng cách ghi đè các metatables hoặc truy cập trực tiếp các biến toàn cục) để giám sát và trích xuất dữ liệu từ các bảng này.
*   **Các điểm dữ liệu chính**: Việc trích xuất tập trung vào các yếu tố trò chơi quan trọng:
    *   Bài trên tay người chơi (ID bài, chất, hạng).
    *   Joker đang hoạt động (tên, hiệu ứng, ID duy nhất).
    *   Thẻ Tarot và Planet.
    *   Nội dung/số lượng bài còn lại trong bộ bài.
    *   Lịch sử bài đã chơi và đã bỏ.
    *   Điểm số hiện tại, thông tin blind, tiền cược.
    *   Nội dung cửa hàng.
    *   Các modifier/thử thách toàn cục.
*   **Theo sự kiện**: Việc trích xuất không liên tục mà theo sự kiện, được kích hoạt bởi các hành động quan trọng trong trò chơi để giảm thiểu tác động đến hiệu suất (ví dụ: sau khi một lá bài được chơi, một ván bài được rút, một vòng kết thúc, cửa hàng được mở).

### 5.2. Tuần tự hóa JSON trong Lua (`src/lua_game_hooks/socket_client.lua`)

*   **Tiêu chuẩn hóa**: Bảng Lua đã trích xuất đại diện cho trạng thái trò chơi được chuyển đổi thành một chuỗi JSON tiêu chuẩn. Điều này tuân thủ lược đồ được định nghĩa trong `src/common/game_state_schema.lua`, đảm bảo rằng phía Python có thể phân tích dữ liệu một cách đáng tin cậy.
*   **Công cụ**: Lua thường yêu cầu các thư viện bên ngoài để tuần tự hóa JSON mạnh mẽ (ví dụ: `dkjson` hoặc triển khai tùy chỉnh nếu các ràng buộc về kích thước nghiêm ngặt). Client `Luasocket` quản lý chuyển đổi này trước khi gửi.
*   **Vận chuyển**: Chuỗi JSON đã tuần tự hóa sau đó được gửi qua socket TCP đến Bộ điều phối Python.

### 5.3. Giải tuần tự hóa JSON trong Python (`src/python_orchestrator/communication/socket_server.py`)

*   **Tiếp nhận**: `socket_server.py` lắng nghe các kết nối TCP đến và nhận chuỗi JSON.
*   **Phân tích và xác thực**: Chuỗi JSON đã nhận được phân tích cú pháp thành một từ điển Python hoặc một mô hình Pydantic (nếu sử dụng lược đồ nghiêm ngặt). Việc xác thực dựa trên `src/common/game_state_schema.py` đảm bảo tính toàn vẹn và nhất quán của dữ liệu, bắt các vấn đề tiềm ẩn từ phía Lua.

### 5.4. Chuyển đổi trạng thái trò chơi thành truy vấn RAG (`src/python_orchestrator/rag_model/rag_processor.py`)

*   **Trích xuất đặc trưng**: Đối tượng trạng thái trò chơi Python đã giải tuần tự hóa được phân tích để xác định các đặc trưng và thực thể chính cần thông tin ngữ cảnh.
*   **Truy vấn RAG**: Các đặc trưng này tạo thành cơ sở của các truy vấn đến ChromaDB để truy xuất các quy tắc trò chơi, mô tả thẻ bài hoặc các cơ chế khác có liên quan.
*   **Xây dựng lời nhắc**: Ngữ cảnh đã truy xuất được kết hợp với trạng thái trò chơi hiện tại và các hướng dẫn của LLM để xây dựng lời nhắc cuối cùng. Một ví dụ về cấu trúc:

    ```
    "Trạng thái trò chơi Balatro hiện tại: {json_game_state}

    Kiến thức trò chơi liên quan (từ cơ sở dữ liệu):
    {retrieved_context_about_jokers_and_rules}

    Dựa trên trạng thái trò chơi hiện tại và các quy tắc Balatro liên quan, hãy gợi ý nước đi tối ưu tiếp theo. Phản hồi của bạn PHẢI ở định dạng JSON:
    {
      "action": "play_hand" | "discard_cards",
      "cards_to_play": ["<card_id>", ...],
      "cards_to_discard": ["<card_id>", ...],
      "reasoning": "...",
      "expected_score_chips": <number>,
      "expected_score_mult": <number>
    }
    Nếu không có nước đi tối ưu, hãy gợi ý "wait". Nếu có lỗi, xuất "error" với "message".
    "
    ```

## 6. Chuyển đổi dữ liệu: LLM sang Lua

Phần này bao gồm cách các gợi ý của LLM được Python xử lý và cuối cùng được hiển thị trở lại trong trò chơi.

### 6.1. Đầu ra và phân tích LLM (`src/python_orchestrator/api_client/lm_studio_client.py`)

*   **Đầu ra JSON có cấu trúc**: LLM được hướng dẫn tạo phản hồi ở định dạng JSON nghiêm ngặt (như trong ví dụ lời nhắc ở trên). Điều này rất quan trọng để phân tích cú pháp lập trình và độ tin cậy.
*   **Tiếp nhận phản hồi**: `lm_studio_client.py` nhận đầu ra văn bản thô từ API LM Studio.
*   **Phân tích và xác thực JSON**: Đầu ra thô được phân tích cú pháp thành một đối tượng Python. Xử lý lỗi mạnh mẽ được triển khai ở đây để bắt:
    *   **JSON không đúng định dạng**: Nếu LLM đi chệch khỏi cấu trúc JSON được yêu cầu.
    *   **Gợi ý vô nghĩa**: Nếu nội dung trong JSON không đúng logic (ví dụ: gợi ý chơi một lá bài không có trên tay).
    *   **Lỗi API**: Các vấn đề với chính API LM Studio.
*   **Xử lý lỗi**: Trong trường hợp đầu ra không đúng định dạng hoặc vô nghĩa, bộ điều phối Python sẽ ghi lại lỗi và gửi một tin nhắn "Gợi ý thất bại" đơn giản hóa trở lại trò chơi Lua.

### 6.2. Định dạng hiển thị từ Python sang Dòng lệnh Love2D

*   **Thông tin chi tiết có thể hành động**: Gợi ý LLM đã phân tích được xử lý để trích xuất thông tin quan trọng nhất cho người chơi (ví dụ: hành động được đề xuất, các lá bài liên quan và điểm số dự kiến).
*   **Định dạng ngắn gọn**: Với không gian hạn chế và tính chất tạm thời của dòng lệnh trò chơi, gợi ý được định dạng ngắn gọn.
*   **Truyền trở lại Lua**: Gợi ý đã định dạng (hoặc một thông báo lỗi) được gửi trở lại client trò chơi Lua, có thể thông qua cùng một socket TCP hoặc một kênh phản hồi chuyên dụng.
*   **Hiển thị trong trò chơi (`src/lua_game_hooks/init.lua`)**:
    *   Tập lệnh Lua nhận tin nhắn đã định dạng.
    *   Nó phân tích tin nhắn (nếu đó là JSON đơn giản hóa hoặc chuỗi).
    *   Sau đó, nó sử dụng API đồ họa của Love2D để hiển thị văn bản gọn gàng trên dòng lệnh trong trò chơi, đảm bảo khả năng hiển thị và dễ đọc mà không làm gián đoạn trò chơi.

## 7. Công nghệ chính

*   **Balatro (Công cụ Love2D)**: Môi trường trò chơi, cung cấp ngữ cảnh cho trợ lý.
*   **LuaJIT 2.1**: Ngôn ngữ lập trình được sử dụng để trích xuất và giao tiếp dữ liệu trong trò chơi.
*   **Luasocket**: Thư viện Lua cho giao tiếp socket TCP.
*   **Python 3.13.12**: Ngôn ngữ chính cho bộ điều phối, logic AI và hệ thống RAG.
*   **FastAPI**: Khung web Python để xây dựng các điểm cuối API và xử lý giao tiếp từ Lua.
*   **Uvicorn**: Máy chủ ASGI để chạy ứng dụng FastAPI.
*   **LM Studio**: Máy chủ suy luận cục bộ để chạy LLM, cung cấp API tiêu chuẩn.
*   **ChromaDB**: Cơ sở dữ liệu nhúng mã nguồn mở để xây dựng cơ sở tri thức RAG.
*   **Nhúng Vector**: Biểu diễn số của văn bản nắm bắt ý nghĩa ngữ nghĩa, cho phép truy xuất hiệu quả thông tin liên quan.

## 8. Thách thức kỹ thuật và giải pháp

Dự án này giải quyết một số thách thức phức tạp, thể hiện khả năng giải quyết vấn đề mạnh mẽ:

### 8.1. Chuyên môn tích hợp hệ thống

*   **Thách thức**: **Tích hợp sâu vào trò chơi & Độ ổn định**: Tương tác với trạng thái nội bộ của trò chơi đang chạy (bảng Lua `G`) thông qua runtime hooking mà không gây ra lỗi hoặc vấn đề về hiệu suất. Đảm bảo tính mô-đun cho các bản vá trò chơi trong tương lai.
    *   **Giải pháp**: Kịch bản Lua tỉ mỉ tập trung vào các hook tối thiểu, theo sự kiện. Kiểm thử rộng rãi (unit và tích hợp) để xác thực độ ổn định. Thiết kế mô-đun của các tập lệnh Lua (`data_extractor.lua`, `socket_client.lua`) cho phép cập nhật cô lập.
*   **Thách thức**: **Giao tiếp giữa các tiến trình độ trễ thấp**: Truyền dữ liệu thời gian thực giữa Lua (trò chơi) và Python (bộ điều phối) trong khi vẫn duy trì sự trôi chảy của trò chơi.
    *   **Giải pháp**: Triển khai socket TCP qua `localhost` để giao tiếp trực tiếp, nhanh chóng. Tối ưu hóa tuần tự hóa/giải tuần tự hóa JSON để giảm thiểu chi phí. Máy chủ Python không đồng bộ (FastAPI) xử lý các yêu cầu hiệu quả.
*   **Thách thức**: **Chi phí hiệu suất**: Ngăn chặn tình trạng giảm FPS hoặc độ trễ đầu vào đáng chú ý trong Balatro mặc dù chạy các tiến trình bên ngoài.
    *   **Giải pháp**: Các hook Lua được điều khiển bởi sự kiện, không liên tục thăm dò. Bộ điều phối Python được thiết kế để hoạt động hiệu quả (FastAPI, thư viện nhẹ). Kiểm tra stress (`test_resource_usage.py`) và giám sát hiệu suất (`performance_monitor.py`) rất quan trọng để xác định và tối ưu hóa các nút thắt cổ chai.

### 8.2. Kỹ năng kỹ thuật AI

*   **Thách thức**: **RAG hiệu quả cho chiến lược trò chơi**: Xây dựng hệ thống RAG cung cấp lời khuyên chính xác, phù hợp với ngữ cảnh cho một trò chơi phức tạp như Balatro.
    *   **Giải pháp**: **Phân đoạn dựa trên thực thể** trong ChromaDB đảm bảo truy xuất nguyên tử các yếu tố trò chơi cụ thể (Joker, quy tắc). `data_processor.py` và `knowledge_base_builder.py` tự động hóa việc tạo cơ sở tri thức. `rag_processor.py` truy vấn DB một cách thông minh dựa trên trạng thái trò chơi.
*   **Thách thức**: **Kỹ thuật lời nhắc để xuất ra có cấu trúc**: Yêu cầu LLM liên tục trả về các gợi ý chiến lược ở định dạng JSON nghiêm ngặt, có thể phân tích được.
    *   **Giải pháp**: Hướng dẫn rõ ràng, tường minh trong lời nhắc, cùng với các ví dụ lược đồ JSON và hình phạt cho việc không tuân thủ (nếu được API của LLM hỗ trợ). Phân tích cú pháp và xác thực mạnh mẽ ở phía Python (`lm_studio_client.py`) để xử lý các sai lệch.
*   **Thách thức**: **Suy luận AI độ trễ thấp**: Đạt được các gợi ý chiến lược trong vòng vài giây (mục tiêu 3-5 giây) từ đầu đến cuối.
    *   **Giải pháp**: Sử dụng LLM cục bộ thông qua LM Studio (loại bỏ độ trễ mạng đối với các API đám mây). Tối ưu hóa truy xuất RAG từ ChromaDB. Client API hiệu quả cho LM Studio.
*   **Thách thức**: **Tiêu chuẩn hóa và độ mạnh của dữ liệu**: Đảm bảo biểu diễn dữ liệu nhất quán giữa Lua, Python và đầu vào/đầu ra của LLM. Xử lý các phản hồi LLM hoặc dữ liệu trò chơi không đúng định dạng.
    *   **Giải pháp**: Định nghĩa một lược đồ `game_state_schema` nghiêm ngặt (cả trong Lua và Python). Xác thực mở rộng ở mỗi bước chuyển đổi dữ liệu. Cơ chế ghi lỗi và dự phòng (ví dụ: thông báo "Gợi ý thất bại") để duy trì độ ổn định của hệ thống.

## 9. Kỹ năng được thể hiện trong phỏng vấn

Dự án này làm nổi bật một bộ kỹ năng mạnh mẽ được đánh giá cao trong các vai trò kỹ thuật phần mềm và AI:

*   **Tích hợp hệ thống**:
    *   Tích hợp các hệ thống khác nhau (trò chơi Lua, ứng dụng Python, LM Studio, ChromaDB).
    *   Giao tiếp đa ngôn ngữ (Lua-Python qua socket).
    *   Runtime hooking và sửa đổi các ứng dụng hiện có.
    *   Hiểu và tôn trọng các ràng buộc của hệ thống bên ngoài (độ ổn định của trò chơi).
*   **Kỹ thuật AI**:
    *   Thiết kế và triển khai hệ thống RAG cho kiến thức miền cụ thể.
    *   Xây dựng và quản lý cơ sở tri thức (ChromaDB, nhúng vector).
    *   Kỹ thuật lời nhắc cho hành vi LLM mong muốn và đầu ra có cấu trúc.
    *   Làm việc với suy luận LLM cục bộ (LM Studio) để bảo mật và hiệu suất.
    *   Đánh giá và giảm thiểu các thách thức cụ thể của AI (độ trễ, ảo giác, định dạng đầu ra).
*   **Kiến trúc & Thiết kế phần mềm**:
    *   Nguyên tắc thiết kế mô-đun (tách biệt mối quan tâm trong Lua và Python).
    *   Thiết kế hệ thống theo sự kiện.
    *   Cân nhắc khả năng mở rộng (mặc dù cục bộ, kiến trúc hỗ trợ phân phối).
    *   Tiêu chuẩn hóa dữ liệu theo lược đồ.
*   **Tối ưu hóa hiệu suất**:
    *   Xác định và giải quyết các nút thắt cổ chai hiệu suất trong các hệ thống thời gian thực.
    *   Hiểu tác động của các tiến trình bên ngoài đến các ứng dụng chính (FPS trò chơi).
    *   Xử lý và giao tiếp dữ liệu hiệu quả.
*   **Giải quyết vấn đề & Gỡ lỗi**:
    *   Giải quyết các vấn đề phức tạp, đa thành phần trên các ngôn ngữ và môi trường khác nhau.
    *   Chiến lược xử lý lỗi và ghi nhật ký mạnh mẽ.
    *   Thiết kế cho các trường hợp biên và hành vi không mong muốn.
*   **Kỹ thuật dữ liệu**:
    *   Đường ống trích xuất, chuyển đổi và tải (ETL) dữ liệu cho cơ sở tri thức.
    *   Tuần tự hóa và giải tuần tự hóa dữ liệu trên các hệ thống không đồng nhất.
    *   Định nghĩa và thực thi lược đồ.