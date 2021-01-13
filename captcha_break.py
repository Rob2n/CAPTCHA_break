#! /usr/bin/env python3

import argparse
from typing import final
from numpy.core.numeric import _full_like_dispatcher, full
import requests
import base64
from bs4 import BeautifulSoup
import pytesseract
import cv2
import numpy as np
from string import punctuation
import os
import re
import letter_mode
import utils

BENCHMARK = False
OFFLINE = False
SAVE = 0

def recognize_captcha(img_path): # solve captcha as a full block of text
	img = cv2.imread(img_path, 0)
	custom_config = r'-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 12' # character whitelist + psm 12 -> Assume sparse text
	img_to_string = pytesseract.image_to_string(img, config=custom_config)
	# Below is code to get confidence data on solves and more, dev only
	# img_to_letter = pytesseract.image_to_data(img, config=custom_config, output_type=pytesseract.Output.DICT) # get confidence data and more
	# confidence = img_to_letter['conf'][-1], img_to_letter['text'][-1]
	return img_to_string.strip()[:12]

def get_captcha(filename): # download captcha from challenge website
	s = requests.Session()
	try:
		first_r = s.get("http://challenge01.root-me.org/programmation/ch8/") # Must be connected to rootme.org to get a response
	except:
		print("Error when connecting to https://root-me.org website.\nAre you logged into the site ?\n")
		print("If you don't want to do online CAPTCHA solving, do :\n\t./captcha_break --offline")
		exit()
	soup = BeautifulSoup(first_r.text, 'html.parser')
	img_tags = soup.find_all('img')
	url = [img['src'] for img in img_tags][0] # Parse to get captcha data
	with open(filename, 'wb') as f:
		f.write(base64.b64decode(url[22:])) # Save captcha to disk from b64
	with open('captcha_untreated.png', 'wb') as f:
		f.write(base64.b64decode(url[22:])) # Save untreated captcha to disk from b64
	return s, first_r

def treat_captcha(filename): # denoise captcha image
	image = cv2.imread(filename)
	image[np.where((image==[0,0,0]).all(axis=2))] = [255,255,255] # Remove pixel noise
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # Convert result to graysclae
	image = cv2.copyMakeBorder(image, 8, 8, 8, 8, cv2.BORDER_CONSTANT, value=[255, 255, 255]) # Add some padding to image
	if OFFLINE:
		cv2.imwrite(filename[:-4] + "_treated" + filename[-4:], image) # Save treated image
		return filename[:-4] + "_treated" + filename[-4:]
	else:
		cv2.imwrite(filename, image) # Save treated image
		return filename

def send_captcha(s, first_r, solved_captcha): # send the solved captcha to site
	url = 'http://challenge01.root-me.org/programmation/ch8/'
	payload = {'cametu': solved_captcha}
	r = s.post(url, data=payload, cookies=first_r.cookies, allow_redirects=True)
	print("Sent : ", solved_captcha)
	return r

def run(): # run captcha solving using full word method
	filename = "captcha.png" # temporary filename for captcha treatment
	s, first_r = get_captcha(filename) # return Session object and first response for later use
	treat_captcha(filename) # denoise captcha image
	solved_captcha = recognize_captcha(filename) # solve captcha using word mode
	r = send_captcha(s, first_r, solved_captcha) # send solve response
	if 'Congratz' in r.text: # If Congratz is in the response, we responded with a valid captcha and quickly enough
		utils.save_valid_captcha(solved_captcha)
		return 0
	else:
		return 1

def benchmark_mode(): # classic benchmark mode on 100 requests
	attempts = 100
	good = 0
	for attempt in range(attempts):
		res = run()
		if res == 0:
			good += 1
	print('Good: {}\nBad: {}\nScore: {}%'.format(good, attempts-good, (good/attempts)*100))
	exit()

def save_captchas(): # -s : just save captchas to disk, no recognition
	if not os.path.exists('saved_captchas'):
		os.makedirs('saved_captchas')
	for nb in range(SAVE):
		filename = "saved_captchas/{}.png".format(nb)
		get_captcha(filename)
		treat_captcha(filename)
	exit()

def offline_solve(folder): # solve captchas located in "folder"
	if not os.path.exists(folder):
		print("[Error]\n\t./offline_captchas folder not found, creating it ...\n")
		os.makedirs(folder)
		print("Please put your unsolved CAPTCHAs in there and run :\n\t./captcha_break -o")
	captchas_path = os.listdir(folder) # list captchas in dir
	if not captchas_path:
		print("No CAPTCHA found in ./offline_captchas")
	for captcha in captchas_path:
		captcha_path = os.path.join(folder, captcha)
		if "treated" not in captcha_path:
			print("Found untreated file: " + captcha_path)
			treated_captcha_path = treat_captcha(captcha_path) # denoise captcha images
			solved_captcha = recognize_captcha(treated_captcha_path) # solve captcha using word mode
			print("Guessed text : " + solved_captcha)
			if len(solved_captcha) < 12:
				print('Less than 12 characters recognized, the guessed text is most likely wrong.')
	exit()

def main():
	if BENCHMARK:
		benchmark_mode() # Run benchmark on 100 requests
		# letter_mode.benchmark_letter_mode() # Run benchmark in letter mode on local files (run normal benchmark one time and then this if you want to test)
	elif SAVE:
		save_captchas() # -s: save unsolved captchas to disk
	elif OFFLINE:
		offline_solve('offline_captchas')
	else:
		res = run()
		if res == 0:
			print('Successfully recognized :)')
		else:
			print('Recognition failed :(')

def handle_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-b", "--benchmark", help="make a benchmark on 100 recognitions", action='store_true')
	parser.add_argument("-s", "--save", help="save <SAVE> captchas to disk (for ML dataset, offline demo solving, etc)", type=int)
	parser.add_argument("-o", "--offline", help="solve offline CAPTCHAs located in offline_captchas folder", action='store_true')
	args = parser.parse_args()
	global BENCHMARK
	BENCHMARK = args.benchmark
	global SAVE
	SAVE = args.save
	global OFFLINE
	OFFLINE = args.offline

if __name__ == "__main__":
	handle_args()
	main()