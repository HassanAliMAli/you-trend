## Conversation Log

- User provided console logs showing 400 Bad Request for `/api/trends`.
- Identified that `api_key` is `null` in the request to the backend.
- `ApiContext.js` logs show `localStorage.getItem('youtube_api_key')` returning `null` at the time of the API call.
- Hypothesized that the API key is either not being saved correctly or is being cleared unintentionally.
- Added a `console.log` to `ApiProvider`'s `useEffect` to check the API key's initial state in `localStorage` when the context mounts.
- Updated `CHANGELOG.md`. 