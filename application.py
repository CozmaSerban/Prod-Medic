from genericpath import exists
from bson import json_util
from operator import le, methodcaller
from flask import Flask, request, redirect, url_for, render_template, session
import pymongo, json
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from auth import auth
from bson.json_util import dumps
import logging
import xlsxwriter

client = pymongo.MongoClient("mongodb+srv://serban:serban@cluster0.oi6hu.mongodb.net/?retryWrites=true&w=majority")
db = client.get_database('medic')
records = db.patients
tb_analize = db.analize

medicatii = {
    "interferon_beta":[
        {"analiza":"AST, ALT", "perioada":[{"luna": 0, "count":1},{"luna": 1, "count":2},{"luna": 3, "count":2},{"luna": 6, "count":99}]},
        {"analiza":"HLG", "perioada":[{"luna": 0, "count":1},{"luna": 1, "count":1},{"luna": 3, "count":1},{"luna": 6, "count":99}]},
        {"analiza":"Hormoni tiroidieni (TSH, fT3, fT4)", "perioada":[{"luna": 0, "count":1},{"luna": 6, "count":99}]},
        {"analiza":"RMN", "perioada":[{"luna": 0, "count":1},{"luna": 12, "count":99}]},
    ],
    "glatiramer_acetat":[
        {"analiza":"AST, ALT", "perioada":[{"luna": 0, "count":1},{"luna": 12, "count":99}]},
        {"analiza":"HLG", "perioada":[{"luna": 0, "count":1},{"luna": 12, "count":99}]},
        {"analiza":"Hormoni tiroidieni (TSH, fT3, fT4)", "perioada":[{"luna": 0, "count":1},{"luna": 12, "count":99}]},
        {"analiza":"RMN", "perioada":[{"luna": 0, "count":1},{"luna": 12, "count":99}]},
    ],
    "fingolimod":[
        {"analiza":"hemograma","perioada":[{"luna": 0, "count":1}]},
        {"analiza":"BT","perioada":[{"luna": 0, "count":1}]},
        {"analiza":"GGT ECG","perioada":[{"luna": 0, "count":1}]},
        {"analiza":"ac anti-VZV","perioada":[{"luna": 0, "count":1}]},
        {"analiza":"AST, ALT", "perioada":[{"luna": 0, "count":1},{"luna": 3, "count":1},{"luna": 6, "count":1},{"luna": 9, "count":1},{"luna": 12, "count":99}]},
        {"analiza":"HLG", "perioada":[{"luna": 0, "count":1},{"luna": 3, "count":1},{"luna": 6, "count":1},{"luna": 12, "count":99}]},
        {"analiza":"FO", "perioada":[{"luna": 0, "count":1},{"luna": 3, "count":99}]},
        {"analiza":"dermatologic", "perioada":[{"luna": 0, "count":1},{"luna": 6, "count":1},{"luna": 12, "count":1}]},
        {"analiza":"RMN", "perioada":[{"luna": 12, "count":99}]},   
    ],
    "terliflunomida":[
        {"analiza":"TB", "perioada":[{"luna": 0, "count":1}]},
        {"analiza":"HLG", "perioada":[{"luna": 0, "count":1},{"luna": 6, "count":99}]},
        {"analiza":"AST, ALT, BT, FAL, GGT", "perioada":[{"luna": 0, "count":1},{"luna": 1, "count":6}]},
        {"analiza":"TA", "perioada":[{"luna": 6, "count":99}]},
        {"analiza":"RMN", "perioada":[{"luna": 12, "count":99}]},
    ],
    "dimetil_fumarate":[
        {"analiza":"AST, ALT, BT, FAL, GGT", "perioada":[{"luna": 0, "count":1},{"luna": 6, "count":1},{"luna": 12, "count":99}]},
        {"analiza":"HLG", "perioada":[{"luna": 0, "count":1},{"luna": 3, "count":1},{"luna": 6, "count":1},{"luna": 12, "count":99}]},
        {"analiza":"RMN", "perioada":[{"luna": 12, "count":99}]},
        {"analiza":"Creatinina/Uree/Sumar urina", "perioada":[{"luna": 0, "count":1},{"luna": 3, "count":1},{"luna": 6, "count":99}]},
    ],
    "ocrelizumab":[
        {"analiza":"RMN", "perioada":[{"luna": 12, "count":99}]},
        {"analiza":"Ag HBS, Ac HBC,Ac HbS ac VHC, Ac HIV, ac VZV, Quantiferon TBC", "perioada":[{"luna": 0, "count":1}]},
    ],
    "natalizumab":[
        {"analiza":"AST, ALT, GGT, FAL", "perioada":[{"luna": 12, "count":99}]},
        {"analiza":"RMN", "perioada":[{"luna": 12, "count":99}]},
        {"analiza":"Indice JC", "perioada":[{"luna": 0, "count":1},{"luna": 6, "count":99}]},
    ],
    "alemtuzumab":[
        {"analiza":"HLG", "perioada":[{"luna": 0, "count":1},{"luna": 1, "count":99}]},
        {"analiza":"Creatinina", "perioada":[{"luna": 0, "count":1},{"luna": 1, "count":99}]},
        {"analiza":"Sumar de urina si urocultura", "perioada":[{"luna": 0, "count":1},{"luna": 1, "count":99}]},
        {"analiza":"TSH, fT3, fT4", "perioada":[{"luna": 0, "count":1},{"luna": 3, "count":99}]},
        {"analiza":"Examen dermatologic", "perioada":[{"luna": 0, "count":1},{"luna": 12, "count":99}]},
        {"analiza":"RMN", "perioada":[{"luna": 12, "count":99}]},
    ],
    "siponimod":[
        {"analiza":"HLG", "perioada":[{"luna": 0, "count":1},{"luna": 6, "count":99}]},
        {"analiza":"AST, ALT, BT", "perioada":[{"luna": 0, "count":1},{"luna": 6, "count":99}]},
        {"analiza":"Ac VZV", "perioada":[{"luna": 0, "count":1}]},
        {"analiza":"Examen oftalmologic", "perioada":[{"luna": 0, "count":1}]},
        {"analiza":"ECG ", "perioada":[{"luna": 0, "count":1}]},
        {"analiza":"sumar de urina plus urocultura", "perioada":[{"luna": 0, "count":1}]},
        {"analiza":"RMN", "perioada":[{"luna": 24, "count":99}]},
    ]


}

app = Flask(__name__)
app.secret_key = "super secret key"
# app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=2)
app.register_blueprint(auth)


@app.route("/")
def index():
    if "email" in session:
        return render_template("index.html")
    else:
        return redirect(url_for("auth.login"))

@app.route("/patients")
def patients():
    if "email" in session:
        return render_template("patients.html")
    else:
        return redirect(url_for("auth.login"))

@app.route("/add_patient", methods=["POST"])
def add_patient():
    data = request.get_json(force=True)
    
    #needs check for duplicates
    data["medic"] = session["email"]
    if is_unique(records,"cnp",data['cnp']):
        for key in medicatii:
            if key[:3] == data["tratament"].lower()[:3]:
                    data["analize"] = medicatii[key]
        for analiza in data["analize"]:
            for entry in analiza["perioada"]:
                now = datetime.now()
                new = now + relativedelta(months=entry["luna"])
                entry["time"] = str(new.month)+"/"+str(new.year)

        records.insert_one(data)
        print("Your data{}".format(data))
        add_analize(data=data)
    else:
        print("Patient {} already exists".format(data['cnp']))
    
    return "asdasd"

@app.route("/add_patient_existent", methods=["POST"])
def add_patient_existent():
    print("Delete is executed")
    
    data = request.get_json(force=True)
    start_date = str(data["start_time"])
    print(start_date)
    timp_initial = datetime.strptime(start_date, '%m/%Y')
    now = datetime.now()
    timp = str(now.month)+"/"+str(now.year)
    timp_acum = datetime.strptime(timp, '%m/%Y')
    delta = relativedelta(timp_acum, timp_initial)
    total_luni  = delta.months + (delta.years * 12)


    data["medic"] = session["email"]
    if is_unique(records,"cnp",data['cnp']):
        for key in medicatii:
            if key[:3] == data["tratament"].lower()[:3]:
                    data["analize"] = medicatii[key]

        for analiza in data["analize"]:
            for entry in analiza["perioada"]:

                entry["time"] = str(timp_initial.month)+"/"+str(timp_initial.year)
   
        for analiza in data["analize"]:
                timp_intermediar = timp_initial
                total_months = total_luni
                for timp in analiza["perioada"]:
                    if timp["count"] !=0:       
                        if total_months >= 1 and timp["luna"] == 0:
                            timp["count"] = 0
                        else:
                            full_months = total_months // timp["luna"]
                            if full_months > timp["count"]:
                                timp_intermediar = timp_intermediar + relativedelta(months=(timp["count"])*int(timp["luna"]))
                                total_months = total_months - (timp["count"] * timp["luna"])
                                timp["count"] = 0
                                timp["time"] = str(timp_intermediar.month)+"/"+str(timp_intermediar.year)
                            elif full_months == timp["count"]:
                                now = datetime.now()
                                timp["time"] = str(now.month)+"/"+str(now.year)
                                timp["count"] = 1
                                total_months = 0
                            elif full_months !=0:
                                timpul = timp_intermediar + relativedelta(months=(full_months+1)*int(timp["luna"]))
                                timp["time"] = str(timpul.month)+"/"+str(timpul.year)
                                timp["count"] = timp["count"] - full_months
                                total_months = total_months - (full_months * timp["luna"])


        records.insert_one(data)
        print("Your data{}".format(data))
        add_analize(data=data)
    
    else:
        print("Patient {} already exists".format(data['cnp']))
    
    return "asdasd"
           
    

@app.route("/update_patient", methods=["POST"])
def update_patient():
    data = request.get_json(force=True)
    print(data)
    #needs check for duplicates
    myquery = { "cnp": data["cnp"] }
    newvalues = { "$set": { "nume": data["nume"] ,"cnp":data["cnp"], "prenume": data["prenume"], "extranotite": data["extranotite"]} }
    records.update_one(myquery, newvalues)    
    return "asdasd"

@app.route("/get_patient", methods=["GET"])
def get_patient():
    print(list(records.find({},{ "medic": session["email"] })))
    
    data = dumps(list(records.find({ "medic": session["email"] })))
    return data

@app.route("/get_record", methods=["GET"])
def get_record():

    update_records()
    print(list(tb_analize.find({},{ "medic": session["email"] })))
    now = datetime.now()
    print(str(now.month)+"/"+str(now.year))
    
    data = dumps(list(tb_analize.find({ "medic": session["email"] })))
    return data

def update_records():
    print("Updating records..")
    now = datetime.now()
    timp = str(now.month)+"/"+str(now.year)
    tb_analize.delete_many({ "medic": session["email"] })
    patients = list(records.find({ "medic": session["email"] }))
    for patient in patients:
        for analiza in patient["analize"]:
            for period in analiza["perioada"]:
                if period["count"] != 0:
                    if timp == period["time"]:
                        record = {}
                        record["medic"] = patient["medic"]
                        record["cnp"] = patient["cnp"]
                        record["nume"] = patient["nume"]
                        record["prenume"] = patient["prenume"]
                        record["analiza"] = analiza["analiza"]
                        record["tratament"] = patient["tratament"]
                        record["time"] = period["time"]
                        print("To be inserted {}".format(record))
                        tb_analize.insert_one(record)
    
@app.route("/generate_xls", methods=["GET"])
def generate_xls():
    workbook = xlsxwriter.Workbook('patients.xlsx')
    worksheet = workbook.add_worksheet()
    row = 0
    col = 0
    print("")
    return "alskdmas"



@app.route("/delete_patient", methods=["POST"])
def delete_patient():
    print("Delete is executed")
    data = request.get_json(force=True)
    records.delete_one({"cnp":data['cnp']})
    tb_analize.delete_many({"cnp":data['cnp']})
    #fix refresh page
    return render_template("patients.html")

@app.route("/checked_analiza", methods=["POST"])
def check_analiza():
    print("Delete is executed")
    now = datetime.now()
    acum = str(now.month)+"/"+str(now.year)
    data = request.get_json(force=True)
    tb_analize.delete_one({"cnp":data['cnp'], "analiza":data["analiza"]})
    patient = list(records.find({"cnp":data['cnp']}))[0]
    records.delete_one({"cnp":data['cnp']})
    analize = patient["analize"]
    for analiza in analize:
        if analiza["analiza"] == data["analiza"]:
            for  i,timp in enumerate(analiza["perioada"]):
                # print(type(timp["count"]))
                if str(timp["time"]) == str(acum) and int(timp["count"]) != 0:
                    update_date = datetime.now()
                    updated = update_date + relativedelta(months=timp["luna"]) #se face update la timp in baza de date si se face -- la counter
                    timp["time"]= str(updated.month)+"/"+str(updated.year)
                    timp["count"] = timp["count"] - 1
                    if timp["count"] == 0:
                        try:
                            updt = updated + relativedelta(months=analiza["perioada"][i+1]["luna"])
                            analiza["perioada"][i+1]["time"] =  str(updt.month)+"/"+str(updt.year)
                        except:
                            timp["count"] = 99
           
    records.insert_one(patient)
    return render_template("patients.html")



@app.route("/details_patient", methods=["GET"])
def details_patient():
    print("Details is executed")
    args = request.args
   
    data = records.find({"cnp": args["cnp"]})
    data = list(data)
    info = "Nu sunt date!"
    try:
        info = data[0]["extranotite"]
    except:
        print("NU SUNT INFO")
        
    
    #fix refresh page
    return {"notes": info}

@app.route("/change_patient", methods=["GET"])
def change_patient():
    print("CHANGE DETAUKS is exeai cuted")
    args = request.args
   
    data = records.find({"cnp": args["cnp"]})
    data = list(data)
    print(data[0])

    #fix refresh page
    return json.dumps(data[0], indent=4, default=json_util.default)



#used to add data to analize table from add_patient form 
def add_analize(data):
    analize = data["analize"]
    now = datetime.now()
    print(now)
    datum = str(now.month)+"/"+str(now.year)
    for analiza in analize:
        for period in analiza["perioada"]:
            if period["count"] != 0:
                if datum == period["time"]:
                    print(period)
                    print(datum)
                    print(period["time"])
                    record = {}
                    record["medic"] = data["medic"]
                    record["cnp"] = data["cnp"]
                    record["nume"] = data["nume"]
                    record["prenume"] = data["prenume"]
                    record["analiza"] = analiza["analiza"]
                    record["tratament"] = data["tratament"]
                    record["time"] = period["time"]
                    print("To be inserted {}".format(record))
                    tb_analize.insert_one(record)
 

    
   

def is_unique(collection,field, value):
    
    #result = collection.count_documents({"\""+field+"\"": value})
    result = collection.count_documents({field: value})
    if result == 0:
        return True
    else:
        return False

