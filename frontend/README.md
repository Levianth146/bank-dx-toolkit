# Dashboard đối sánh chuyển đổi số ngân hàng

Frontend React + TypeScript cho dashboard DBI–DTI. Tab Tổng quan đọc điểm và
chỉ số trực tiếp từ API read-only của dự án backend
[bank-dx-toolkit](https://github.com/Levianth146/bank-dx-toolkit).

## Chạy cùng backend

1. Khởi động API backend theo hướng dẫn trong `api/README.md` của repo
   bank-dx-toolkit (mặc định `http://localhost:8000`).
2. Tại thư mục frontend, chạy:

   ```powershell
   npm install
   npm run dev
   ```

Frontend gọi API tại `http://localhost:8000/api/v1`. Để dùng địa chỉ khác,
đặt biến môi trường `VITE_API_BASE_URL`, ví dụ:

```text
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Tab Tổng quan sử dụng `/meta`, `/ranking`, `/trend` và
`/banks/{bank}/{year}`. Tab Hồ sơ ngân hàng cũng đọc `/dti-inputs?bank=...&year=...`
để hiển thị các số liệu đã đối chiếu từ báo cáo tài chính, kèm liên kết nguồn và
số trang. Bộ lọc năm/ngân hàng, biểu đồ xu hướng, radar, phân bố điểm rubric và
các số liệu báo cáo đều dựa trên phản hồi của backend; không có số liệu dashboard
được giả lập ở frontend. Dữ liệu thiếu được giữ là trạng thái chưa có dữ liệu,
không tự đổi thành 0.

Nếu không kết nối được API, hãy kiểm tra backend đang chạy và cấu hình CORS.

---

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is enabled on this template. See [this documentation](https://react.dev/learn/react-compiler) for more information.

Note: This will impact Vite dev & build performances.
You can also try [the experimental native React Compiler support in plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md#rust-react-compiler) by using `compiler: true` in the plugin options instead of using the Babel plugin.

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])

```

You can also install [eslint-plugin-react-x](https://npmx.dev/package/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://npmx.dev/package/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])

```
