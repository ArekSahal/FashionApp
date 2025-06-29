# Handling /search_outfit API Response in the Frontend

This guide explains how your frontend should robustly handle the response from the `/search_outfit` endpoint, including best practices, error handling, and code examples.

---

## 1. Make the API Request

Use `fetch` or your preferred HTTP client to POST the prompt to `/search_outfit`:

```js
const response = await fetch('https://fashionapp-production-facd.up.railway.app/search_outfit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  body: JSON.stringify({ prompt: userPrompt })
});
```

---

## 2. Check the HTTP Status

Before parsing the response, check if the HTTP status is OK (200):

```js
if (!response.ok) {
  // Handle HTTP errors (network, server, etc.)
  const errorText = await response.text();
  throw new Error(`API request failed: ${response.status} - ${errorText}`);
}
```

---

## 3. Parse the JSON Response

Parse the response body as JSON:

```js
const data = await response.json();
console.log("API response:", data); // For debugging
```

---

## 4. Validate the Response Structure

The backend returns a structure like:

```json
{
  "success": true,
  "results": [
    {
      "idea_name": "...",
      "idea_description": "...",
      "tags": [...],
      "products": [ ... ]
    },
    ...
  ]
}
```

**Check for success:**

```js
if (!data.success) {
  // The backend ran but returned an error (e.g., parsing failed)
  throw new Error(data.error || "Unknown error from API");
}
```

---

## 5. Handle the Results

Assuming `data.success` is `true`:

```js
const outfits = data.results; // This is an array of outfit objects

if (!Array.isArray(outfits) || outfits.length === 0) {
  // No outfits found, show a friendly message
  showMessage("No outfits found for your prompt. Try a different description!");
  return;
}

// Process and display the outfits
outfits.forEach(outfit => {
  // Each outfit has: idea_name, idea_description, tags, products
  displayOutfit(outfit); // Implement this function to render the outfit in your UI
});
```

---

## 6. Handle Products in Each Outfit

Each `outfit.products` is an array of product objects matching your `FashionItem` interface.  
You can map or display them as needed:

```js
outfit.products.forEach(product => {
  // Render product details (name, image, price, etc.)
  displayProduct(product); // Implement this function for your UI
});
```

---

## 7. Error Handling and User Feedback

- **Network errors:** Catch and display a user-friendly message.
- **API errors:** Show the error message from the backend if available.
- **Empty results:** Inform the user if no outfits/products are found.

Example:

```js
try {
  // ...fetch and process as above...
} catch (error) {
  showMessage(error.message || "Something went wrong. Please try again.");
}
```

---

## 8. Example: Full Flow

```js
async function searchOutfit(prompt) {
  try {
    const response = await fetch('https://fashionapp-production-facd.up.railway.app/search_outfit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ prompt })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API request failed: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || "Unknown error from API");
    }

    const outfits = data.results;
    if (!Array.isArray(outfits) || outfits.length === 0) {
      showMessage("No outfits found for your prompt. Try a different description!");
      return;
    }

    outfits.forEach(displayOutfit);

  } catch (error) {
    showMessage(error.message || "Something went wrong. Please try again.");
  }
}
```

---

## 9. Debugging Tips

- Always log the raw response for debugging: `console.log("API response:", data);`
- If you see unexpected errors, check the browser console for stack traces.
- If you get a 200 response but no data, inspect the `data` object for error messages or empty results.

---

## 10. TypeScript Interface Example

If you use TypeScript, define interfaces for type safety:

```ts
interface FashionItem { /* ... as in your code ... */ }
interface Outfit {
  idea_name: string;
  idea_description: string;
  tags: string[];
  products: FashionItem[];
}
interface SearchResponse {
  success: boolean;
  results?: Outfit[];
  error?: string;
  details?: string;
}
```

---

## Summary Table

| Step                | What to Do                                      |
|---------------------|------------------------------------------------|
| Make request        | POST JSON to `/search_outfit`                  |
| Check status        | Ensure `response.ok` is true                    |
| Parse JSON          | `const data = await response.json()`            |
| Check `success`     | If `!data.success`, show error                  |
| Handle results      | If `data.results` is array, display outfits     |
| Handle errors       | Catch and show user-friendly error messages     |

---

If you follow this flow, your frontend will robustly handle all valid and error responses from your backend! 