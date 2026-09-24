# Uploads

Use the dedicated bundled command whenever an image, video, or audio input
exists only on the local machine, or when a supported inline value would exceed
its published size limit. A remote tool cannot read a local path.

```text
python3 scripts/mcp_client.py upload <path> --mime-type <type>
```

Supply one regular file with its exact MIME type and byte length. The command
obtains and validates a single-use `beatra.assets.upload` grant,
rejects redirects, performs the exact HTTP PUT with the returned headers and
unchanged bytes, validates the HTTP PUT response body, and prints the resulting
artifact reference. It does not send the Beatra credential to the upload host.

Pass the returned artifact ID or media object to the chosen generation tool.
Never pass a filesystem path, replace the bundled command with host HTTP, or
manually call the raw grant tool and reproduce its PUT flow. The grant result is
not the artifact: the artifact exists only after the command completes the
upload and validates the response.

The general upload ceiling is 100 MB. A selected model can advertise a lower
size, duration, MIME-type, or media-role limit through `beatra.models.list`;
respect that current interface card. Requesting the dedicated command again is
the safe recovery when a grant expires. Never reuse a grant for another file,
change the returned headers, or alter the file bytes.

Ordinary image, video, and audio upload does not require a generic rights
attestation. A voice sample intended for `beatra.voices.clone` is different:
obtain explicit confirmation that the user owns the voice or has the owner's
permission before upload and before setting `consent_attested: true`.
