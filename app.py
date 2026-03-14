from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.get("/health-check")
def health() :
    return {"message" : "API Working"}


@app.post("/image-analyzer")
def image_analyzer(file : UploadFile = File(...)) :
    return {
        "filename" : file.filename,
        "content_type" : file.content_type
    }