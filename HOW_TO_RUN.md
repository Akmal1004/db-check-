# How to Run the FastAPI Endpoint

This guide explains how to use the code in `fastapi_endpoint.py` and run your FastAPI application.

### Background

The file `fastapi_endpoint.py` was created to give you the complete, corrected code for the scraper trigger endpoint. **It is not meant to be run directly.**

The intended workflow is for you to **copy the code from `fastapi_endpoint.py`** and **paste it into your main FastAPI application file** (the one that contains your `app = FastAPI()` instance and your other routes).

---

### Step 1: Integrate the Code

1.  **Open `fastapi_endpoint.py`** and review the code.
2.  **Open your main FastAPI application file** (e.g., `main.py`, `app.py`, or whichever file contains your other routes).
3.  **Copy the necessary imports** from the top of `fastapi_endpoint.py` into your main application file. Make sure to verify the import paths to match your project structure, especially for `ScreenerLogRepository`.
4.  **Copy the `trigger_nextday_watchlist_scraper` function** from `fastapi_endpoint.py` and paste it into your main application file along with your other routes. Make sure it uses your `app` instance (e.g., the `@app.get(...)` decorator).

---

### Step 2: Install `uvicorn`

To run a FastAPI application, you need an ASGI server. The standard server is `uvicorn`. If you don't have it installed, open your terminal and run:

```bash
pip install uvicorn
```

---

### Step 3: Run the FastAPI Server

1.  Open your terminal in the root directory of your project.
2.  Run the server using `uvicorn`. You need to tell it the location of your main application file and the `app` instance.

    For example, if your main file is named `main_api.py` and the `FastAPI` instance inside it is named `app`, you would run:

    ```bash
    uvicorn main_api:app --reload
    ```
    *(Replace `main_api` with the name of your Python file without the `.py` extension)*.

    The `--reload` flag is optional, but it's very helpful during development as it automatically restarts the server whenever you save a change to the code.

---

### Step 4: Access the Endpoint

1.  Once the server is running, `uvicorn` will show you the address where it's live, usually `http://127.0.0.1:8000`.
2.  Open your web browser and go to `http://127.0.0.1:8000/docs`. This will open the interactive API documentation (Swagger UI).
3.  In the documentation, you should see a section for "Watchlist Scrapers" and the endpoint `/watchlist/trigger_nextday_scraper`.
4.  You can expand it, click "Try it out", and then "Execute" to run your scraper.
