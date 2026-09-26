#!/usr/bin/env python3
"""Start Atomic Office on the loopback interface.

Inicia Atomic Office en la interfaz local.
"""

import os

import uvicorn


if __name__ == "__main__":
    port = int(os.getenv("OFFICE_PORT", "8765"))
    print(f"Atomic Office: http://127.0.0.1:{port}", flush=True)
    uvicorn.run("office.web:app", host="127.0.0.1", port=port)
