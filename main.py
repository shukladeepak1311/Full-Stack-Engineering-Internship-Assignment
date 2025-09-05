from fastapi import Depends, FastAPI,  UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Annotated, List
import os 
from pydantic import BaseModel
#import pymupdf - used built in pdf reader of llamaindex 
from fastapi.responses import JSONResponse
from huggingface_hub import login
from llama_index.llms.huggingface import HuggingFaceInferenceAPI
from llama_index.core import PromptTemplate
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import StorageContext, load_index_from_storage
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request



app = FastAPI()

#to server react index.js file 
templates = Jinja2Templates(directory="./build")
app.mount('/static', StaticFiles(directory="./build/static"), 'static')
@app.get('/render')
async def render(req: Request):
    return templates.TemplateResponse('index.html',{'request':req})


#global variable to store the auth token
HF_TOKEN = ""

queryEngine =  ""

#enabling cors for using with react development server
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#to get the pdfs present in the uploads directory in document form 
def getDocuments():
    reader = SimpleDirectoryReader(input_dir="./uploads")
    documents = reader.load_data()
    return documents
    
#to get the embed model 
def getEmbedModel():
    embed_model = HuggingFaceEmbedding(model_name = "BAAI/bge-small-en-v1.5")
    return embed_model

#to get the llm model api object 
def getLLM():
    llm = HuggingFaceInferenceAPI(model_name = "mistralai/Mistral-7B-Instruct-v0.3", token = HF_TOKEN )
    return llm


#to set query engine or retrieve the engine from the saved vector index 
def setQueryEngine():
    try :
        current_path = os.getcwd()
        folderPath = os.path.join(current_path, "indexing_storage")
        persist_dir = "./indexing_storage"
        storage_context = StorageContext.from_defaults(persist_dir= persist_dir)
        global queryEngine
        if os.path.exists(folderPath):
            new_vector_index = load_index_from_storage(storage_context, embed_model = getEmbedModel())
            retriever = VectorIndexRetriever(index=new_vector_index, similarity_top_k=5)
            query_engine = new_vector_index.as_query_engine(llm=getLLM())
            queryEngine = query_engine
        else :
            vector_index = VectorStoreIndex.from_documents(getDocuments(), embed_model=getEmbedModel())
            query_engine = vector_index.as_query_engine(llm=getLLM())
            persist_dir = "./indexing_storage"
            vector_index.storage_context.persist(persist_dir= persist_dir)
            queryEngine = query_engine
    except Exception as e:
        print(e)
            # return query_engine


#to update the indexing if new file is uploaded 
async def updateIndexing():
    global queryEngine
    vector_index = VectorStoreIndex.from_documents(getDocuments(), embed_model=getEmbedModel())
    query_engine = vector_index.as_query_engine(llm=getLLM())
    persist_dir = "./indexing_storage"
    vector_index.storage_context.persist(persist_dir= persist_dir)
    queryEngine = query_engine





@app.get("/")
async def root():
    """
    endpoint to check is the server is up and running
    """
    return {"message": "Hello World"}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """endpoint to upload file in pdf format"""
    try:
        file_name = file.filename
        # print(file_name)
        save_directory = "uploads"
        Path(save_directory).mkdir(parents=True, exist_ok=True)
        with open(f"{save_directory}/{file_name}", "wb") as f:
            f.write(await file.read())
        await updateIndexing()
        # setData(alltext)
        return JSONResponse(content={"message": "File uploaded successfully"}, status_code=200)
    except Exception as e:
        print(e)
        return JSONResponse(content={"message": f"Failed to upload file: {str(e)}"}, status_code=500)


@app.get("/retrain")
async def retrain():
    """not implemented"""
    try:
        # get_text()
        # retrain_model()
        return JSONResponse(content={"message": "File uploaded successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"{str(e)}"}, status_code=500)
    

class TokenInput(BaseModel):
    """simple class representing a token"""
    token: str

@app.post("/login/")
async def loginLLM(token1 : TokenInput):
    """login using the token from huggingFace """
    try:
        print(token1)
        token = token1.token
        global HF_TOKEN
        HF_TOKEN = token
        print(HF_TOKEN)
        login(token= HF_TOKEN)
        print(HF_TOKEN)
        setQueryEngine()
        return JSONResponse(content={"message": "logged in successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"Failed to login {e}"}, status_code=500)


class QuestionInput(BaseModel):
    """class representing a question asked """
    question: str

@app.post("/talk/")
async def talk(question_input: QuestionInput):
    """the endpint to ask questions regarding the PDF"""
    question = question_input.question
    query_engine = queryEngine
    response = str(query_engine.query(question))
    return {"message": response, "id": 100 }


"""Other implementations of talk please ignore """



# @app.get("/talk/{question}")
# async def talk(question:str):
#     text = DATA
#     qa_template = getTemplate()
#     prompt = qa_template.format(context_str = text, query_str = question)
#     llm = getLLM()
#     response = llm.complete(prompt)
#     print(response)
#     return JSONResponse(content={"message": f"{response}"}, status_code=200)


# @app.get("/talk/{question}")
# async def talk(question:str):
#     text = DATA
#     qa_template = getTemplate()
#     prompt = qa_template.format(context_str = text, query_str = question)
#     llm = getLLM()
#     response = llm.complete(prompt)
#     print(response)
#     return JSONResponse(content={"message": f"{response}"}, status_code=200)



# @app.post("/talk/")
# async def talk(question_input: QuestionInput):
#     question = question_input.question
#     text = DATA
#     qa_template = getTemplate()
#     prompt = qa_template.format(context_str=text, query_str=question)
#     llm = getLLM()
#     response = llm.complete(prompt)
#     print(response)
#     return {"message": response.text, "id": 100 }



# def getTemplate():
#     """ Not using the template noe since using vector indexes is better """
#     template = (
#     "We have provided context information below. \n"
#     "---------------------\n"
#     "{context_str}"
#     "\n---------------------\n"
#     "Given this information, please answer the question: {query_str}\n"
#     )
#     qa_template = PromptTemplate(template)
#     return qa_template
