# -------------------------------------------------------------
#  Gittxt-web production image
# -------------------------------------------------------------
#  • Installs OS build tools once
#  • Caches Python deps in a separate layer
#  • Installs the *already-published* gittxt package
#  • Installs gittxt_web itself (editable or normal)
# -------------------------------------------------------------

# ---------- base ----------
    FROM python:3.12-slim AS base
    ENV PYTHONUNBUFFERED=1 \
        PIP_NO_CACHE_DIR=1
    
    # system packages
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
            build-essential git && \
        rm -rf /var/lib/apt/lists/*
    
    WORKDIR /app
    
    # ---------- deps layer ----------
    # 1. upgrade pip / wheel
    RUN pip install --upgrade pip setuptools wheel
    
    # 2. core dependency already on PyPI
    RUN pip install gittxt>=1.7.7
    
    # 3. project dependencies (declared in pyproject or requirements)
    COPY pyproject.toml poetry.lock* requirements.txt* ./ 
    
    # ––– choose ONE of the following –––
    # If you adopted a  **pyproject.toml**  as recommended:
    RUN pip install .[all]  # or:  pip install -e .  during dev
    # …else fall back to requirements.txt
    # RUN pip install -r requirements.txt
    
    # ---------- app code ----------
    COPY . .
    
    EXPOSE 8000
    CMD ["uvicorn", "gittxt_web.main:app", "--host", "0.0.0.0", "--port", "8000"]
    