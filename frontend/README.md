# FoodHub frontend

This Vite/React frontend is connected to the FastAPI backend in the parent
project. During development, Vite proxies `/api` to `http://127.0.0.1:8000`.

Start the backend first:

```powershell
cd D:\APP\foodhub\backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Then start the frontend in a second terminal:

```powershell
cd D:\APP\foodhub\frontend
npm install
npm run dev
```

Open `http://127.0.0.1:3000`. The browser flow is:

1. Register or log in. The opaque Bearer token is saved in local storage.
2. Load/save the user's long-term preference profile.
3. Upload one to five JPEG, PNG, or WebP menu pages to `/api/menu/scan`.
4. Display translated dish fields in the saved preferred language.
5. Send `menu_id` plus current-meal choices to `/api/recommendations`.

Set `VITE_API_BASE_URL` only when the API is not served through the local Vite
proxy. Copy `.env.example` to `.env.local` for a custom value.

Checks:

```powershell
npm run build
npm run lint
```
