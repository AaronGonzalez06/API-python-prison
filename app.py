from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime,date
from typing import Text, Optional
from uuid import uuid4 as uuid
from fastapi.responses import FileResponse
from io import BytesIO

savesPrisioners = []
app = FastAPI()

class Prisioner(BaseModel):
    id: str
    name: str
    surname: Optional[str]
    age: str
    dni: str
    created_at: datetime = datetime.now()
    detection: Text
    
class Incidence(BaseModel):
    dni: str
    incidence: Text
    created_at: datetime = datetime.now()

@app.get('/')
def welcome():
    return {"message": "Prisoner consultation application."}

@app.get('/prisioners')
def prisoners():
    if len(savesPrisioners) == 0:
        return {"message": "Nothing for now."}
    else:
        return savesPrisioners

@app.get('/prisioner/{minAge}/{maxAge}')
def Search_prisioner_age(minAge: str,maxAge: str):
    filterPrisioners = []
    for prisioner in savesPrisioners:
        if prisioner["age"] >= minAge and prisioner["age"] <= maxAge:
            filterPrisioners.append(prisioner)
    if len(filterPrisioners) != 0:
        return {
                    "total": len(filterPrisioners),
                    "prisioner": filterPrisioners
                }
    else:
        raise HTTPException(status_code=404, detail="No search results")

@app.get('/prisionerDate/{mindate}/{maxdate}')
def Search_prisioner_date(mindate: date,maxdate: date):
    filterPrisioners = []
    for prisioner in savesPrisioners:
        dateAux = prisioner["created_at"].date()
        if dateAux >= mindate and dateAux <= maxdate:
            filterPrisioners.append(prisioner)
    if len(filterPrisioners) != 0:
        return {
                    "total": len(filterPrisioners),
                    "prisioner": filterPrisioners
                }
    else:
        raise HTTPException(status_code=404, detail="No search results")

@app.get('/prisionerDetection/{detection}')
def Search_prisioner_detection(detection: str):
    filterPrisioners = []
    for prisioner in savesPrisioners:
        if detection in prisioner["detection"]:
            filterPrisioners.append(prisioner)
    if len(filterPrisioners) != 0:
        return {
                    "total": len(filterPrisioners),
                    "prisioner": filterPrisioners
                }
    else:
        raise HTTPException(status_code=404, detail="No search results")

@app.get('/prisioner/{dni}')
def Search_prisioner(dni: str):
    for prisioner in savesPrisioners:
        if prisioner["dni"] == dni:
            return prisioner
    raise HTTPException(status_code=404, detail="No prisoner has been found with DNI: " + dni)

@app.post('/save')
def Saved_prisioner(prisioner: Prisioner):
    for x in savesPrisioners:
        if x["dni"] == prisioner.dni:
            return {"message": "Prisoner already registered with DNI " + prisioner.dni}
    prisioner.id = uuid()
    savesPrisioners.append(prisioner.model_dump())
    return prisioner.model_dump()

@app.delete('/prisioner/{dni}')
def Delete_prisioner(dni: str):
    for index,prisioner in enumerate(savesPrisioners):
        if prisioner["dni"] == dni:
            savesPrisioners.pop(index)
            return {"message": "Eliminated prisoner: " + dni}
    raise HTTPException(status_code=404, detail="No prisoner has been found with DNI: " + dni)

@app.put('/prisioner/{dni}')
def Update_prisioner(dni:str, updatePrisioner:Prisioner):
    for prisioner in savesPrisioners:
        if prisioner["dni"] == dni:
            prisioner["name"] = updatePrisioner.name
            prisioner["surname"] = updatePrisioner.surname
            prisioner["age"] = updatePrisioner.age
            prisioner["detection"] = updatePrisioner.detection                    
            return {
                    "message": "Updated prisoner",
                    "prisioner": prisioner
                    }
    raise HTTPException(status_code=404, detail="No prisoner has been found with DNI: " + dni)

@app.get("/downloadReport")
def Download_report():
    orderPrisioners = sorted(savesPrisioners, key=lambda prisioner: prisioner['dni'])
    with open("report.txt", "w") as archivo:
        for prisioner in orderPrisioners:
            archivo.write(f"DNI: {prisioner['dni']}, Name: {prisioner['name']}, Surname: {prisioner['surname']}, Age: {prisioner['age']}\n")
            archivo.write(f"-------------------- Detection --------------------\n")
            archivo.write(f"{prisioner['detection']}\n")
            archivo.write(f"\n")
    return FileResponse("report.txt", filename="report.txt")

@app.get("/downloadReportPrisoner/{dni}")
def Download_report_prisioner(dni:str):
    orderPrisioners = sorted(savesPrisioners, key=lambda prisioner: prisioner['dni'])
    with open("report.txt", "w") as archivo:
        for prisioner in orderPrisioners:
                if prisioner['dni'] == dni:
                    archivo.write(f"DNI: {prisioner['dni']}, Name: {prisioner['name']}, Surname: {prisioner['surname']}, Age: {prisioner['age']}\n")
                    archivo.write(f"-------------------- Detection --------------------\n")
                    archivo.write(f"{prisioner['detection']}\n")
                    archivo.write(f"\n")
                    return FileResponse("report.txt", filename="report.txt")
    raise HTTPException(status_code=404, detail="No prisoner has been found with DNI: " + dni)

@app.get("/downloadIncidence")
def Download_incidence():
    return FileResponse("incidence.txt", filename="incidence.txt")

@app.post("/addIncidence")
def add_incidence(incidence:Incidence):
    print(incidence)
    for prisioner in savesPrisioners:
        if prisioner["dni"] == incidence.dni:
            with open("incidence.txt", "a") as archivo:
                archivo.write(f"DNI: {incidence.dni}\n")
                archivo.write(f"-------------------- Incidence --------------------\n")
                archivo.write(f"{incidence.incidence}\n")
                archivo.write(f"\n")
                return {"message": "Added incidence"}
        else:
            raise HTTPException(status_code=404, detail="No prisoner has been found with DNI: " + incidence.dni)        