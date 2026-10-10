# Public delivery compatibility repair

The user screenshots showed the original capped film. The original stable video URL remained an October 9 asset (33,640,352 bytes) while fresh-page checks selected the latest hash-named film. This was a publication compatibility gap; the precise state of the user browser cache is not observable.

Atomically replaced the stable MP4 and poster with the current reviewed assets under the exclusive publication lock, with backup at FX99 `/home/derek/backups/known-world-publish/20261010-delivery-compatibility`. Release manifest now includes stable aliases. `export/publication.py` packages these aliases on each future release. No service configuration or restart, no render, no benchmark, no source recount.

HTTPS downloads of both stable and hashed video URLs match SHA256 `7fdfb10711d7a5eab6aed4a866365c7b065817a59dccc07a5208f2dc3224ef57`; poster aliases also match. The desktop browser explicitly played the stable URL and decoded its ending; portrait checked the hash URL. Both show the current aggregate counts without page errors or horizontal overflow. Inspected actual decoded desktop ending. Packaging generated all four assets with equal alias hashes. Evidence in `validation/`.

Already decoded frames in an open tab cannot be changed remotely. Open the entry URL with `?v=20261010-1708` to bypass a cached entry page and select the current hashed film. Server cache policy was not changed: Caddy configuration is root-owned, and this repair needs no elevated action.
