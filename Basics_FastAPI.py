from fastapi import FastAPI,Path,Query,Body,Form,File,UploadFile,Cookie,Header
from fastapi.responses import PlainTextResponse
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import os

from pydantic import BaseModel


from hashlib import sha256
from base64 import b64encode

import uvicorn
import shutil





class MyJsonBodyModel(BaseModel):
    salt:str = ''
    password:str =''





app = FastAPI()

app.mount('/static',StaticFiles(directory='fastapi_static'),'staticfiles')
templates_server = Jinja2Templates('templates')





#Path Basic usage
@app.get('/path_basic/{text}')
async def getHash(text:str=Path(min_length=1)):
    h = sha256(text.encode()).digest()
    return {'base64': b64encode(h).decode(),'hex':h.hex()}


#Query Basic usage
@app.get('/query_basic')
async def getbase64(text:str=Query(min_length=1)):
    return {'base64': b64encode(text.encode()).decode()}







#-----------------------------------------------------------------------

# handling json Body request using BaseModel
@app.post('/json_body_model')
async def handleBodybyModel(b:MyJsonBodyModel):
    return {'password_hash':sha256(bytes(b.salt+b.password,'utf-8')).hexdigest()}


# handling json Body request using nested BaseModel
class Info(BaseModel):
    name:str
    age:int

class Person(BaseModel):
    user_info:Info
    email:str

@app.post('/info') # request body is like {"user_info":{"name":"shifat","age":10000},"email":"shifat@gmail.com"}
def getPerson(p:Person):
    return PlainTextResponse(content=f'Your Name is {p.user_info.name} and Age {p.user_info.age}.Email: {p.email}')
    




# handling json Body request using Body(). use Body(embed=True) for single json key value pair
@app.post('/json_body')
async def handleOneBody(b:str=Body(embed=True,alias='text')):
    return {'Length':len(b)}





# handling json Body request using Body() for multiple json key value pair. 
@app.post('/json_body_V2')
async def handleBody(salt:str=Body(),passkey:str=Body(alias='password')):
    return  {'base64': b64encode(bytes(salt+passkey,'utf-8')).decode()}






# handling json Body request using Body() and Basemodel combined .request body is like {"b": {"salt": "nacl2","password": "pwd"},"text": "nacl"}
@app.post('/json_body_V3')
async def handleBody3(b:MyJsonBodyModel,s:str=Body(alias='text')):
    return  {'password_hash':sha256(bytes(b.salt+b.password,'utf-8')).hexdigest(),'Length':len(s)}




#handling Form body
@app.post('/form_body')
async def handleForm(name:str=Form(),age:int=Form()):
    return {'name':name,'age':age}



#handling File Upload
@app.post('/file')
async def handleForm(fp:UploadFile = File(alias='file')):
    with open(fp.filename,'wb') as fp2:
        shutil.copyfileobj(fp.file,fp2)
    return {'FileName':fp.filename}



#-----------------------------------------------------------------------











#=========================================================================================================================================
#handling cookies and headers 


#setting Headers and cookies
@app.get('/get_cookies_headers')
async def getCookiesAndHeader(r:Request):
    res = PlainTextResponse(content="The cookie and Header is set",headers={'X-Secret': 'mysecret',"X-Name":'shifat'})
    res.set_cookie('server_path',os.getcwd())
    print(str(r))
    return res 



#accessing headers and cookies using Request model. (easy)
@app.get('/check_cookies_headers')
async def getCookiesAndHeader(r:Request):
    content = ''
    server_path = r.cookies.get('server_path','')
    username = r.headers.get('x-name','') # headers are always lowercase
    secret = r.headers.get('x-secret','') # headers are always lowercase

    if username == 'shifat' and secret == 'mysecret':
        content = 'I know You '
    else:
        content = 'Who are you? '+username
    
    if server_path != '':
        content += f'Last Current Directory of server was {server_path} when you visited'
    
    res = PlainTextResponse(content=content)
    return res



#accessing headers and cookies using Header() , Cookie()
@app.get('/check_cookies_headers_V2')
async def getCookiesAndHeader2(username : Optional[str] = Header('',alias='x-name'),secret : Optional[str] = Header('',alias='x-secret'),server_path:str = Cookie('')):
    content = ''

    if username == 'shifat' and secret == 'mysecret':
        content = 'I know You '
    else:
        content = 'Who are you? '+username
    
    if server_path != '':
        content += f'Last Current Directory of server was {server_path} when you visited'
    
    res = PlainTextResponse(content=content)
    return res

#-------------------------------------------------------------------------------------------------------------------------------



#Server Template

@app.get('/files')
def getFiles(r:Request):
    l = os.listdir('fastapi_static')
    return templates_server.TemplateResponse('getfiles.html',{'files':l,'request':r})














if __name__ == "__main__":
    uvicorn.run(port=80,app=app,host='127.0.0.1') # To run from command line type -> "uvicorn.exe Basics_FastAPI:app" 