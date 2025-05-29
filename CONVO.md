## Conversation Log

- User provided console logs showing 400 Bad Request for `/api/trends`.
- Identified that `api_key` is `null` in the request to the backend.
- `ApiContext.js` logs show `localStorage.getItem('youtube_api_key')` returning `null` at the time of the API call.
- Hypothesized that the API key is either not being saved correctly or is being cleared unintentionally.
- Added a `console.log` to `ApiProvider`'s `useEffect` to check the API key's initial state in `localStorage` when the context mounts.
- Updated `CHANGELOG.md`.
- User provided new console logs showing `ApiContext: Provider mounted. Initial API key from localStorage: null`, confirming the key is not present in `localStorage` on initial load even after attempting to save it via settings page.
- Inspected `client/src/pages/Settings.js` and found it was using `sessionStorage` instead of `localStorage` and not correctly using `ApiContext` functions.
- Refactored `client/src/pages/Settings.js` to use `localStorage` via `ApiContext` and correctly interface with the context for API key and quota management.
- Updated `CHANGELOG.md` again with the `Settings.js` fix.
- User provided new console logs showing continued `400 Bad Request` and `api_key: null` after previous fixes.
- Confirmed `ApiContext: Provider mounted. Initial API key from localStorage: null` is expected on first load.
- Added `trim()` to `saveApiKey` in `ApiContext.js` and more detailed logging for the save process.
- Added logging to `handleSaveSettings` in `Settings.js` to see the key value before saving.
- Updated `CHANGELOG.md` with these logging and trim enhancements. 