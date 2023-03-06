from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://jain:jain@cluster0.fjuymq7.mongodb.net/?retryWrites=true&w=majority", tls=True,tlsAllowInvalidCertificates=True)
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")[:-2]
    res = MessagingResponse()
    user = users.find_one({"numbers": number})
    if not bool(user):
        res.message("hi, thanks for contacting *The Red Velvet*.\nYou can choose from one of the options below:\n\n "
                    "*Type*\n\n1️⃣ To *Contact* us \n2️⃣ To *Order* snacks \n3️⃣ to know our *Working hours*\n4️⃣ To "
                    "get our *Address*")
        users.insert_one({"numbers": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 1:
            res.message(
                "You can contact us through phone and email.\n\n*Phone*:9310317365 \n*Email*: pythonwp@gmail.com")
        elif option == 2:
            res.message("You have entered *ordering mode*")
            users.update_one({"numbers": number}, {"$set": {"status": "ordering"}})
            res.message(
                "You can select one of the following to order:\n\n1️⃣ Red Velvet \n2️⃣ Dark Forest\n3️⃣ Ice Cream "
                "Cake\n4️⃣ Plum cake\n5️⃣ Sponge Cake\n6️⃣ Genoise Cake\n7️⃣ Carrot Cake\n8️⃣ Butterscotch\n0️⃣ Go "
                "Back")
        elif option == 3:
            res.message("We work everyday from *9AM to 9PM*")
        elif option == 4:
            res.message("We have many centres across the city. Our main center is at *4/54 ,New Delhi*")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 0:
            users.update_one(
                {"number": number}, {"$set": {"status": "main"}})
            res.message("You can choose from one of the options below: "
                        "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                        "To get our *address*")
        elif 1 <= option <= 9:
            cakes = ["Red Velvet Cake", "Dark Forest Cake", "Ice Cream Cake",
                     "Plum Cake", "Sponge Cake", "Genoise Cake", "Angel Cake", "Carrot Cake", "Fruit Cake"]
            selected = cakes[option - 1]
            users.update_one(
                {"number": number}, {"$set": {"status": "address"}})
            users.update_one(
                {"number": number}, {"$set": {"item": selected}})
            res.message("Excellent choice 😉")
            res.message("Please enter your address to confirm the order")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "address":
      
      selected = user["item"]
      res.message("Thanks for shopping with us 😊")
      res.message(f"Your order for *{selected}* has been received and will be delivered to {text} within an hour")
      orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
      users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res.message("Hi, thanks for contacting again.\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                    "To get our *address*")
        users.update_one(
            {"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)



if __name__ == "__main__":
    app.run(port=5000)
