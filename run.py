# run.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", # Busca el objeto 'app' dentro de app/main.py
        host="0.0.0.0",
        port=9000,
        reload=True,
        log_level="info"
    )


    # uvicorn app.main:app --reload --port 9000 --host 0.0.0.0
