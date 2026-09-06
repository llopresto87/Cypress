# Notes

Let's dive in. The cache is not just a store, but a contract with the client.

Additionally, the interplay of the two layers — the router and the renderer — matters here.

The design has three parts — each one described below.

- **Router:** it maps a path to a handler.
- **Renderer:** it turns data into HTML.
- **Store:** it holds the result — for ten minutes.

I hope this helps.

The good news is the store keeps the last value for ten minutes.

Here is a revised version of the note, as requested.
