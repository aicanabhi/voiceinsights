"""Upload limits.

Peak memory per upload is several times the file size, so these caps are what
keep a handful of concurrent uploads from exhausting the box.
"""

MB = 1024 * 1024

# Roughly 50 minutes of mono 64 kbps audio -- comfortably above a normal call.
MAX_UPLOAD_BYTES = 25 * MB

# Read the upload in chunks instead of pulling the whole body into memory.
UPLOAD_CHUNK_BYTES = 1 * MB

# Per-request file cap. Files are only stored here, not transcribed, so this
# bounds request size rather than processing time.
MAX_FILES_PER_REQUEST = 10

ALLOWED_CONTENT_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
    "audio/aac",
    "audio/ogg",
    "audio/webm",
    "audio/flac",
    "audio/x-flac",
}
