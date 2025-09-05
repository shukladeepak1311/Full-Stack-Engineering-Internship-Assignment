
# PDF-query

A simple web application that can help you query the documents you have uploaded in pdf form.
## Installation

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Usage

To run the application, execute:

```bash
uvicorn main:app --reload
```


### API Endpoints

- **Root Endpoint**: Check if the server is up and running.
  - Method: GET
  - Endpoint: `/`
  - Description: endpoint to check if the server is up and running

- **Upload Endpoint**: Upload a PDF file.
  - Method: POST
  - Endpoint: `/upload/`
  - Description: endpoint to upload a PDF file
  - Request Body: Form-data with the file
  - Response: JSON with a success message if the file is uploaded successfully

- **Retrain Endpoint**: Retrain the model. (Not implemented)
  - Method: GET
  - Endpoint: `/retrain`
  - Description: not implemented

- **Login Endpoint**: Login using a token from Hugging Face.
  - Method: POST
  - Endpoint: `/login/`
  - Description: login using the token from Hugging Face
  - Request Body: JSON with a token
  - Response: JSON with a success message if logged in successfully

- **Talk Endpoint**: Ask questions regarding the PDF.
  - Method: POST
  - Endpoint: `/talk/`
  - Description: endpoint to ask questions regarding the PDF
  - Request Body: JSON with a question
  - Response: JSON with the response message and ID

## Documentation

- Swagger Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- GUI: [http://localhost:8000/render](http://localhost:8000/render)


