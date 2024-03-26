Chatbot application

### .env file :
OPENAI_API_KEY=`YOUR_API_KEY`
MONGO_DETAILS= `YOUR_MONGODB_CONNECTION_STRING`

How to run the code 

### Backend
1.  `conda create -n chatbot python=3.10`  
2. `pip install -r requirements.txt`
3. `uvicorn main:app --reload`

### FRONTEND
1. `npm install`
2. `npm run dev`


Chatbot Application will start 

1. In this application user can upload different types of files to chat with including pdf,txt,csv files etc.
2. After uploading text files such as txt and pdf, the text is extracted and converted to embeddings using faiss and openai embeddings and can further used for chatting.
3. For csv file, langchain pandas agent is used to chat and analyzing csv files.
4. Files details and results are stored in mongodb.



### Improvements.
1. chat with Sql database, excel files, json files and more can be implemented using langchain agents.
2. For better results for analyzing state of art models like code Llama 70b - python can be implemented.
3. Can also add vizulalization charts and plot for better understanding using code LLama model.
4. Embedding and its metadata can be effectively stored in vector databases like pinecone.

