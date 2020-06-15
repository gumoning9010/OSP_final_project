#!/usr/bin/python
#-*- coding: utf-8 -*-
import argparse
import subprocess
from flask import Flask, jsonify, request
from flask import render_template 

import re
import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route('/one_output', methods=["POST"])
def name1_check():
	if request.method=="POST":
		url = str(request.form['name'])
		try:
			start = time.time()  # 시작 시간 저장
			
			res = requests.get(url)
			html = BeautifulSoup(res.content, 'html.parser')
    			
			sentences = html.find_all('p')
			word_freq={}
    			
			for i in range(0, len(sentences)):
				word_list = re.sub(u'[^\w\s]','',sentences[i].get_text()) # 특수문자 제거
				word_list = re.sub(r'\b[0-9]+\b\s*', '', word_list) # 숫자로만 이뤄진 단어 제거
        			
				for word in word_list.split():
					if word in word_freq:
						word_freq[word] += 1
					else:
						word_freq[word] = 1
    			
			# value 값 기준으로 key값 정렬    
			word_freq_sorted = {k: v for k, v in sorted(word_freq.items(), key = lambda x: x[1], reverse = True)}
			word_freq_sorted['total_num'] = sum(word_freq.values()) # 전체 단어수
			word_freq_sorted['time'] = time.time() - start  # 현재시각 - 시작시간 = 크롤링 걸린 시간 # 
    			
			result = '크롤링 성공'
		except:    # 예외가 발생했을 때 실행됨
			result='크롤링 실패'
		return render_template('one_output.html', result = result,url = url,
					total_num = word_freq_sorted['total_num'],time_l=word_freq_sorted['time'])


@app.route('/multi_output', methods=["POST"])
def name2_check():
	if request.method=="POST":
		myfibo_num = request.files['profile'].read()
		urls = [x.strip() for x in myfibo_num.decode("utf-8").split(',')]
		
		site_word_freq = {}
		try:
			origin_urls = urls.copy() # 나중에 중복 출력위해 저장
			urls = list(set(urls)) # 중복 url 제거
			
			for url in urls:
				start = time.time()  # 시작 시간 저장
				
				res = requests.get(url)
				html = BeautifulSoup(res.content, 'html.parser')
        			
				sentences = html.find_all('p')
				word_freq={}
        			
				for i in range(0, len(sentences)):
            				
					word_list = re.sub(u'[^\w\s]','',sentences[i].get_text()) # 특수문자 제거
					word_list = re.sub(r'\b[0-9]+\b\s*', '', word_list) # 숫자로만 이뤄진 단어 제거
            				
					for word in word_list.split():
						if word in word_freq:
							word_freq[word] += 1
						else:
							word_freq[word] = 1
        			
				# value 값 기준으로 key값 정렬    
				word_freq_sorted = {k: v for k, v in sorted(word_freq.items(), key = lambda x: x[1], reverse = True)}
				word_freq_sorted['total_num'] = sum(word_freq.values()) # 전체 단어수
				word_freq_sorted['time'] = time.time() - start  # 현재시각 - 시작시간 = 크롤링 걸린 시간 # 
				site_word_freq[url] = word_freq_sorted # 딕트안에 딕트 사이트별로 데이터 정리 
    			
			result = '크롤링 성공'
			overlap = '중복된 url이 존재합니다' if (len(origin_urls) != len(urls)) else "" 
		
		except:    # 예외가 발생했을 때 실행됨
			result = '크롤링 실패'

		return render_template('multi_output.html', result = result,overlap=overlap)



@app.route('/', methods=['GET'])
def hello_hw():
	return render_template('default.html')

if __name__== '__main__':
	try:
		parser = argparse.ArgumentParser(description="")
		parser.add_argument('--listen-port', type=str, required=True, help ="REST service listen port")
		args = parser.parse_args()
		listen_port = args.listen_port
	except Exception as e:
		print('Error: %s' % str(e))
	

	ipaddr=subprocess.getoutput('hostname -I').split()[0]
	print('starting the sevice with ip_add='+ipaddr)
	app.run(debug=False, host=ipaddr, port=int(listen_port))

 
