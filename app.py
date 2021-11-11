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
        'cookie': '__utmc=71379083; iflipsess=palvmg7qnnf2uoie0vt8hed0kj; __utma=71379083.734663800.1635440230.1636492023.1636653592.7; __utmz=71379083.1636653592.7.6.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt=1; __utmb=71379083.2.9.1636653592',
    }

    post_request = 'use_openai=0&meme_id=563423&init_text=&__tok=gvH6kpgsZYvGnuSeEHSdxnEZr%2B2dmZDBrMOfwxUOo9s%3D&__cookie_enabled=1'
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
