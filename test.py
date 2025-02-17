import http.client

conn = http.client.HTTPSConnection("exercisedb.p.rapidapi.com")

headers = {
    'X-RapidAPI-Key': "fe2b80a0fcmsh719764e10f312a9p18c442jsnb5535b4936fe",
    'X-RapidAPI-Host': "exercisedb.p.rapidapi.com"
}

conn.request("GET", "/exercises/target/upper%20back", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
