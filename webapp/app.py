#!/usr/bin/env python
# -*- coding:utf-8 -*-

import base64
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse

from flask import Flask
from flask import abort, jsonify, Response, render_template, request
import MeCab
# from janome.tokenizer import Tokenizer

app = Flask(__name__)
# app.config['JSON_AS_ASCII'] = False

# @app.route('/')
# def hello():
#     return 'Hello world!'

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/listen')
def listen():
  return render_template('exportwav.html')

@app.route('/test')
def test():
  return render_template('test.html')

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

messages = ['Success', 'Faild']

@app.route('/parse', methods=['GET', 'POST'], strict_slashes=False)
def parse():
  try:
    if request.method == 'POST':
        text       = request.form['text']
        dictionary = request.form['dictionary']
    else:
        text       = request.args.get('text', default="", type=str)
        dictionary = request.args.get('dictionary', default="ipadic", type=str)
  except:
        abort(400)
  
  results = mecab_parse(text, dictionary)

  return mecab_response(200, messages[0], results, dictionary)

@app.route('/tokenize', methods=['GET', 'POST'], strict_slashes=False)
def tokenize():
  try:
    if request.method == 'POST':
        text       = request.form['text']
        dictionary = request.form['dictionary']
    else:
        text       = request.args.get('text', default="", type=str)
        dictionary = request.args.get('dictionary', default="ipadic", type=str)
  except:
        abort(400)
  
  results = mecab_tokenize(text, dictionary)

  # return results
  return mecab_response(200, messages[0], results, dictionary)

# @app.errorhandler(400)
# def error400(error):
#     return macab_response(400, messages[1], None, None)

def mecab_response(status, message, results, dictionary):
    return jsonify({'status': status, 'message': message, 'results': results, 'dictionary': dictionary}), status

def mecab_parse(text, dictionary='ipadic'):
    dictionary_dir = "/usr/local/lib/mecab/dic/"
    if dictionary == 'neologd':
        dictionary_name = 'mecab-ipadic-neologd'
    else:
        dictionary_name = dictionary

    m = MeCab.Tagger('-d ' + dictionary_dir + dictionary_name)

    # 出力フォーマット（デフォルト）
    format = ['表層形', '品詞','品詞細分類1', '品詞細分類2', '品詞細分類3', '活用形', '活用型','原型','読み','発音']

    return [dict(zip(format, (lambda x: [x[0]]+x[1].split(','))(p.split('\t')))) for p in m.parse(text).split('\n')[:-2]]

def mecab_tokenize(text, dictionary='ipadic'):
    dictionary_dir = "/usr/local/lib/mecab/dic/"
    if dictionary == 'neologd':
        dictionary_name = 'mecab-ipadic-neologd'
    else:
        dictionary_name = dictionary
    
    # Execute wakati
    m = MeCab.Tagger("-Owakati " + '-d ' + dictionary_dir + dictionary_name)
    result = m.parse(text)
    
    return result

# @app.route('/tokenizer', methods=['GET', 'POST'], strict_slashes=False)
# def tokenizer():
#     if request.method == 'POST':
#         question = request.form['question']
#         
#     else:
#         question = request.args.get('question')
#     
#     # print(urllib.parse.unquote(question))
#     
#     t = Tokenizer()
#     try:
#       tokendata = t.tokenize(urllib.parse.unquote(question))
#     except:
#       return question
#     
#     words=[]
#     for token in tokendata:
#       words.append(token.surface)
#     
#     print(" ".join(words))
#     # question=" ".join(words)
#     
#     # if request.method == 'POST':
#     #   return jsonify(" ".join(words))
#     # else:
#     return jsonify(" ".join(words))

@app.route("/speak", methods=['GET', 'POST'], strict_slashes=False)
def streamwav():
  def generate(text="テキストを入力してください。", emotion='normal', s=44000, p=128, a=0.5, b=0.0, r=1.0, fm=0.0, u=0.5, jm=1.0, jf=1.0, g=0.0, z=0):
    with tempfile.TemporaryDirectory() as tmpdirname:
      open_jtalk = ['open_jtalk']
      mech = ['-x','/usr/local/lib/open_jtalk_dic_utf_8-1.09']
      htsvoice = ['-m','/usr/local/src/mei/mei_' + emotion + '.htsvoice']
      cmd = open_jtalk + mech + htsvoice
      if not s is None:
        sampling_frequency = ['-s ', str(s) ]
        cmd = cmd + sampling_frequency
      
      if not p is None:
        frame_period       = ['-p ', str(p) ]
        cmd = cmd + frame_period
      
      if not a is None:
        all_pass_constant  = ['-a ', str(a) ]
        cmd = cmd + all_pass_constant
      
      postfiltering_coefficient = ['-b ' , str(b) ]
      speech_speed_rate         = ['-r ' , str(r) ]
      additional_half_tone      = ['-fm ', str(fm)]
      voiced_unvoiced_threshold = ['-u ' , str(u) ]
      weight_of_gv_for_spectrum = ['-jm ', str(jm)]
      weight_of_gv_for_log_f0   = ['-jf ', str(jf)]
      volume                    = ['-g ' , str(g) ]
      audio_buffer_size         = ['-z ' , str(z) ]
      outwav = ['-ow',tmpdirname + '/open_jtalk.wav']
      
      cmd = cmd + \
            postfiltering_coefficient + \
            speech_speed_rate + \
            additional_half_tone + \
            voiced_unvoiced_threshold + \
            weight_of_gv_for_spectrum + \
            weight_of_gv_for_log_f0 + \
            volume + \
            audio_buffer_size + \
            outwav
      print(cmd)
      c = subprocess.Popen(cmd,stdin=subprocess.PIPE)
      c.stdin.write(text.encode('utf-8'))
      c.stdin.close()
      c.wait()
      with open(tmpdirname + '/open_jtalk.wav', "rb") as fwav:
        data = fwav.read(1024)
        while data:
          yield data
          data = fwav.read(1024)
  
  try:
    if request.method == 'POST':
        text    = request.form['text']
        emotion = request.form['emotion']
        s       = request.form['s']
        p       = request.form['p']
        a       = request.form['a']
        b       = request.form['b']
        r       = request.form['r']
        fm      = request.form['fm']
        u       = request.form['u']
        jm      = request.form['jm']
        jf      = request.form['jf']
        g       = request.form['g']
        z       = request.form['z']
    else:
        text    = request.args.get('text', default="テキストを入力してください。", type=str)
        emotion = request.args.get('emotion', default="normal", type=str)
        s       = request.args.get('s',  default=44000, type=int)
        p       = request.args.get('p',  default=128,   type=int)
        a       = request.args.get('a',  default=0.5,   type=int)
        b       = request.args.get('b',  default=0.0,   type=float)
        r       = request.args.get('r',  default=1.0,   type=float)
        fm      = request.args.get('fm', default=0.0,   type=float)
        u       = request.args.get('u',  default=0.5,   type=float)
        jm      = request.args.get('jm', default=1.0,   type=float)
        jf      = request.args.get('jf', default=1.0,   type=float)
        g       = request.args.get('g',  default=0.0,   type=float)
        z       = request.args.get('z',  default=0,     type=int)
  except:
        pass
  return Response(generate(text, emotion, s, p, a, b, r, fm, u, jm, jf, g, z), mimetype="audio/x-wav")

@app.route("/upload", methods=['GET', 'POST'], strict_slashes=False)
def upload():
  def recognize(wav):
    with tempfile.TemporaryDirectory() as tmpdirname:
      sox = ['sox']
      rate = ['-r','16000']
      channels = ['-c','1']
      srcwav = [wav]
      name = os.path.basename(wav)
      dstwav = [tmpdirname + '/' + name]
      
      cmd = sox + srcwav + rate + channels + dstwav
      
      print(" ".join(cmd))
      c = subprocess.call(" ".join(cmd), shell=True)
      print(c)
      
      tmplist = tmpdirname + '/' + 'filelist.txt'
      f = open(tmplist,'w')
      f.write("".join(dstwav) + '\n')
      f.close()
      
      print("".join(dstwav))
      
      julius = ['julius']
      am_gmm = ['-C','/usr/local/src/dictation-kit-v4.4/am-gmm.jconf']
      main = ['-C','/usr/local/src/dictation-kit-v4.4/main.jconf']
      input = ['-input','rawfile']
      filelist = ['-filelist',tmplist]
      outfile = ['-outfile']

      cmd = julius + am_gmm + main + input + filelist + outfile
      
      name, ext = os.path.splitext("".join(dstwav))
      outwav = name + '.out'
      
      print(" ".join(cmd))
      c = subprocess.call(" ".join(cmd), shell=True)
      print(c)
      
      print("".join(outwav))
      
      # with open("".join(outwav), 'r') as f:
      #   print(f)
      #   for row in f:
      #     print(row.strip())
      #   return f
      text = ""
      with open(outwav, 'r', encoding='utf-8') as f:
        for row in f:
          # print(row.strip())
          m = re.search(r"sentence1: (?P<text>.*)", row)
          if m:
            return m.group('text')
        return text

  with tempfile.TemporaryDirectory() as tmpdirname:
    # try:
    if request.method == 'POST':
      # print(request.values["fname"])
      # print(request.values["data"])
      wav = tmpdirname + '/' + str(request.values["fname"])
      # wav = '/var/tmp/' + str(request.values["fname"])
      print(wav)
      # the_file = request.values["data"]
      # wav = "./static/wav/" + request.values["fname"]
      # the_file.save(wav)
      # wav = tmpdirname + '/' + "voice.wav"
      with open(wav, 'wb') as f:
        data = request.values["data"].replace('data:audio/wav;base64,', '')
        f.write(base64.b64decode(data))
    else:
      wav = "./static/wav/test.wav"
    # except:
    #   # pass
    #   wav = "./static/wav/test.wav"
    result = recognize(wav)
  return result

# @app.route("/wav")
# def streamwav():
#     def generate():
#         with open("./static/wav/test.wav", "rb") as fwav:
#             data = fwav.read(1024)
#             while data:
#                 yield data
#                 data = fwav.read(1024)
#     return Response(generate(), mimetype="audio/x-wav")


if __name__ == '__main__':
  app.run(host='0.0.0.0')
