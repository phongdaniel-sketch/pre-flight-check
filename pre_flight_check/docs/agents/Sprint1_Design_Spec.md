Sprint1_Design_Spec.md

```
## 1. Overview

Thiết kế UI/UX cho Sprint 1 tập trung vào 4 tính năng chính trong MVP của nền tảng Pre-flight Check nhằm hỗ trợ người dùng upload dữ liệu quảng cáo, phân tích policy tự động qua N8N, đánh giá sáng tạo AI, và dự báo KPI quảng cáo (CPA và ROAS). Giao diện được xây dựng theo phong cách tinh tế, hiện đại, dễ sử dụng, đảm bảo tối ưu hóa chuyển đổi người dùng, đồng thời tương thích tốt với Vue.js, dễ dàng tích hợp backend và Firebase.

## 2. Tổng quan Layout Chính

- Khung layout theo chuẩn Responsive, tối ưu cho màn hình desktop và tablet (Grid system 12 cột)
- Thanh header với logo, tiêu đề, avatar user
- Sidebar thu gọn để điều hướng các tính năng
- Vùng nội dung chính theo luồng sử dụng liên tục: Upload -> Policy Check -> Creative Scoring -> Forecast
- Màu nền #F9FAFB, màu text #212B36, accent #2F80ED, dùng màu cảnh báo đỏ/vàng hợp lý

## 3. Component Chi Tiết

### 3.1 Upload Video / Landing Page Link

- Radio toggle chọn loại upload (video hay link)
- Drag & drop video (mp4, mov), kích thước max 500MB
- Input nhập URL Landing Page, nút kiểm tra validity
- Submit button nổi bật, disabled nếu lỗi, có spinner loading
- Feedback lỗi hiện rõ dưới input

### 3.2 Kết quả Policy Check (N8N)

- Panel kết quả có trạng thái pass/fail với icon màu sắc
- Danh sách chi tiết các chính sách được kiểm tra, trạng thái từng chính sách
- Banner cảnh báo nếu phát hiện vi phạm
- Button xem log chi tiết

### 3.3 AI-Based Creative Scoring

- Card điểm sáng tạo AI nổi bật, điểm số lớn
- Thanh progress bar hiển thị điểm số với animation
- Thông tin chi tiết từng yếu tố con (hình ảnh, tiêu đề, nội dung) dưới dạng badge

### 3.4 Bảng Dự báo CPA & ROAS

- Bảng hiển thị tên quảng cáo, dự báo CPA, ROAS, mức độ tin cậy, gợi ý tối ưu
- Màu sắc thể hiện trạng thái tốt/xấu
- Nút xem chi tiết gợi ý với tooltip hoặc modal
- Phân trang nếu nhiều dữ liệu

## 4. Design System

- Màu nền #F9FAFB, text #212B36, accent #2F80ED, màu lỗi đỏ #D32F2F, cảnh báo vàng nhạt #FFF4E5
- Font Roboto, trọng lượng tiêu đề 700, body text 400-500, khoảng cách tốt cho dễ đọc

## 5. Technical & UX Notes

- Realtime validation, spinner loading chuẩn Vue.js
- Hiển thị trạng thái rõ ràng, accessible, responsive desktop/tablet
- Dễ dàng mở rộng, thêm tính năng theo chuẩn Vue.js

## 6. Wireframe Mô tả

- Header với logo, tên, avatar
- Sidebar gồm các màn hình chính
- Content area gồm các section upload form, policy result, AI creative score, forecast bảng
- Minh họa layout và từng phần chức năng chi tiết

---

Kết luận: Thiết kế UI/UX đầy đủ và chi tiết đáp ứng yêu cầu Sprint 1, tập trung trải nghiệm người dùng hiệu quả và phù hợp với công nghệ sử dụng.

```