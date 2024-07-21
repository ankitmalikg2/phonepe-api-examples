import hashlib
import requests
import base64
import uuid
import json
import constants

def create_sha256_string(input_string):
    sha256_hash = hashlib.sha256(input_string.encode())
    encoded_string = sha256_hash.hexdigest()
    return encoded_string

def string_to_base64(input_string):
    encoded_string = base64.b64encode(input_string.encode())
    return encoded_string.decode()

def phonepePaymentURL(amount: int):

    orderID = "pp-"+str(uuid.uuid4())
    userID = "user-"+str(uuid.uuid4())
    merchantTransactionID = "MT"+str(uuid.uuid4())
    mobileNumber = "9999999998" # test mobile number
    email = "test@gmai.com"

    payload = {
        "amount": amount*100,
        "merchantId": constants.merchant_id,
        "merchantTransactionId": merchantTransactionID,
        "merchantUserId": userID,
        "redirectUrl": constants.webhook_url,
        "redirectMode": "POST",
        "callbackUrl": constants.webhook_url,
        "merchantOrderId": orderID,
        "mobileNumber": mobileNumber,
        "email": email,
        "message": "Payment for " + orderID,
        "paymentInstrument": {
            "type": "PAY_PAGE"
        }
    }
    json_data = json.dumps(payload)
    base64_request = string_to_base64(json_data)

    # X-VERIFY header -- SHA256(Base64 encoded payload + “/pg/v1/pay” + salt key) + ### + salt index
    finalXHeader = create_sha256_string(base64_request + "/pg/v1/pay" + constants.salt_key)+"###"+constants.salt_index

    req = {
        "request": base64_request
    }

    finalHeader = {
        "Content-Type": "application/json",
        "X-VERIFY": finalXHeader
        }
    
    response = requests.post(constants.payment_url, headers=finalHeader, json=req)
    return response


def checkStatus(merchantTransactionID):
    endpoint = constants.status_endpoint +"/"+ constants.merchant_id +"/"+ merchantTransactionID
    url = constants.base_url + endpoint

    finalXHeader = create_sha256_string(endpoint + constants.salt_key)+"###"+constants.salt_index
    my_headers = {
        "Content-Type": "application/json",
        "X-VERIFY": finalXHeader,
        "X-MERCHANT-ID": constants.merchant_id
    }

    response = requests.get(url, headers=my_headers)
    if response.status_code == 200:
        return response.json()
    else:
        return "Something went wrong - " + response.text

    

res = phonepePaymentURL(100)
data = res.json()
print(json.dumps(data))
print()

paymentURL = data["data"]["instrumentResponse"]["redirectInfo"]["url"]
transactionID = data["data"]["merchantTransactionId"]
print("transaction_id - ",transactionID)
print("payment_url - ",paymentURL)
print()


# transactionID = "MTf591a860-53a3-4676-a425-d52ec9404a6e"
# checkStatusResponse = checkStatus(transactionID)
# print(json.dumps(checkStatusResponse))
# print()