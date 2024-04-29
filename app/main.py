import uvicorn

def main():
    uvicorn.run("server.app:app", host="0.0.0.0")

if __name__ == "__main__":
    main()