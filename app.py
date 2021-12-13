import os
import requests
import json
from flask import Flask, render_template, request, redirect, send_file
from s3_functions import list_files, upload_file, show_image
import boto3
import urllib.request

app = Flask(__name__)

LAST_MEME_GEN = ""
BUCKET = os.environ.get('BUCKET_NAME')
TOPIC_ARN = os.environ.get('TOPIC_ARN')
AWS_REGION = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/placement/region').read().decode()

def fetch_meme_string():
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': 'iflipsess=9e78gc9ghkcicd6385p31uug6e; __utma=71379083.1923845604.1639414590.1639414590.1639414590.1; __utmb=71379083.10.9.1639417578369; __utmc=71379083; __utmz=71379083.1639414590.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); G_ENABLED_IDPS=google; G_AUTHUSER_H=0; rootkey=ug_y0XWOLI4burcNaRwUi4YZkg7gCsyC; rootemail=kempel.nathanael%40gmail.com; __utmt=1; _ga=GA1.2.1923845604.1639414590; _gid=GA1.2.1551630543.1639417582; _fbp=fb.1.1639417582654.712570802; __gads=ID=443bf9a167c7cfbd-22bba802e2cc0043:T=1639417583:RT=1639417583:S=ALNI_MYN8scxWhxI8yx2cc-qk1IetuAH8g',
    }

    post_request = 'use_openai=0&meme_id=14371066&init_text=&__tok=rrFXqiETbBPFmKTLqtQccvUmyIgcafR++8QMHTImB8k=&__cookie_enabled=1'
    response = requests.post(
        "https://imgflip.com/ajax_ai_meme",
        data=post_request,
        headers=headers
    )
    result = json.loads(response.text)
    return result['texts']


@app.route("/")
def home():
    global LAST_MEME_GEN
    return render_template('index.html', last_meme_gen=LAST_MEME_GEN)

@app.route("/queue_meme", methods=['POST'])
def queue_meme():
    global LAST_MEME_GEN
    global AWS_REGION

    LAST_MEME_GEN = fetch_meme_string()
    sns = boto3.client("sns", region_name=AWS_REGION)
    sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps(LAST_MEME_GEN)
        )
    return redirect("/")

@app.route("/pics")
def list():
    contents = show_image(BUCKET)
    return render_template('collection.html', contents=contents)

if __name__ == '__main__':
    app.run(debug=True)
