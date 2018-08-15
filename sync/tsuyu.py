import os

from flask import Flask
app = Flask(__name__)

@app.route("/",methods=['POST'])
def req():
    os.system("/media/9da3/rocalyte/private/scripts/anime/sync/quarterly.sh")
    return "Synchronized!\n"

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5932)
