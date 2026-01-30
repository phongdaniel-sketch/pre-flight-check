# Hướng Dẫn Sửa Staging Environment

## Vấn Đề Hiện Tại

Staging environment không thể truy cập được do 2 lý do:

1. **URL cũ không tồn tại:** `https://pre-flight-check-git-develop-phong-daniels-projects.vercel.app`
   - Error: `DEPLOYMENT_NOT_FOUND`
   - Lý do: Deployment đã bị xóa hoặc URL đã thay đổi

2. **URL mới yêu cầu authentication:** `https://pre-flight-check-phong-daniels-projects.vercel.app`
   - Error: `401 Unauthorized`
   - Lý do: Vercel Protection đang bật

## Giải Pháp

### Giải Pháp 1: Tắt Vercel Protection (Khuyến Nghị)

1. Truy cập [Vercel Dashboard](https://vercel.com/dashboard)
2. Chọn project **pre-flight-check**
3. Vào **Settings** → **Deployment Protection**
4. Tắt protection cho **Preview Deployments** (develop branch)
5. Hoặc thêm bypass cho QA testing

**Lưu ý:** Chỉ tắt cho preview deployments, giữ protection cho production nếu cần.

### Giải Pháp 2: Tạo Staging Deployment Riêng

1. Tạo một deployment riêng cho staging không có protection:
   ```bash
   # Cài đặt Vercel CLI
   npm install -g vercel
   
   # Login
   vercel login
   
   # Deploy develop branch
   git checkout develop
   vercel --prod=false
   ```

2. Lưu URL mới vào `/QA/ENVIRONMENTS.md`

### Giải Pháp 3: Sử dụng Production cho Testing (Tạm Thời)

Hiện tại production đang hoạt động tốt và có thể dùng để test:
- URL: `https://pre-flight-check-kohl.vercel.app`
- Tất cả tests đều pass

**Rủi ro:** Test trực tiếp trên production không lý tưởng cho QA process.

## Cập Nhật Environment URLs

Sau khi sửa, cập nhật file `/QA/ENVIRONMENTS.md` với URL chính xác:

```markdown
## 2. Staging Environment (Develop)
Used for QA testing before release. Automatically deployed from the `develop` branch.
- **Primary URL**: [URL mới sau khi fix]
- **Branch**: `develop`
- **Status**: ✅ Active (sau khi sửa)
```

## Kiểm Tra Sau Khi Sửa

Chạy test suite để verify:

```bash
.venv/bin/python QA/run_tests.py --url [STAGING_URL]
```

Expected output:
```
Testing Health Check... ✅ PASSED
Testing Input Validation... ✅ PASSED
Testing Analyze Flow (Happy Path)... ✅ PASSED
Summary: 3/3 tests passed
```

## Thông Tin Vercel Project

- **Project ID:** `prj_xHUGXBTcIMLStLJKde21OcjPkbH7`
- **Org ID:** `team_voE4x04pe3R6F4KBKG6L4uFb`
- **Project Name:** `pre-flight-check`

## Liên Hệ

Nếu không có quyền truy cập Vercel Dashboard, liên hệ với:
- Project owner: phong-daniel
- Team admin để được cấp quyền
