#! /usr/bin/env python3

import os
import cv2
import re
from string import punctuation
from captcha_break import treat_captcha
import numpy as np
import pytesseract

def recognize_captcha_letters(dir_name): # solve the captcha letter by letter
	solved_captcha = ''
	letters = os.listdir(dir_name) # list letters in dir
	letters.sort(key=lambda f: int(re.sub('\D', '', f))) # sort filenames numerically
	for letter in letters:
		img = cv2.imread(os.path.join(dir_name, letter))
		custom_config = r'-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 10' # psm 10 -> single character recognition
		try:
			img_to_letter = pytesseract.image_to_string(img, config=custom_config).strip()[0]
		except:
			continue
		# Below is code to get confidence data on solves and more, dev only
		# img_to_letter = pytesseract.image_to_data(img, config=custom_config, output_type=pytesseract.Output.DICT)
		# print(img_to_letter['conf'][-1], img_to_letter['text'][-1])
		# continue
		solved_captcha += img_to_letter
	return solved_captcha

def validate_letters(solved_captcha, captcha): # verify the score for each captcha character
	# If the recognition is offset by 1 or more letters, the whole captcha comparison will be falsified, this undermines the final score but I have no fix for now as this is a POC
	score = 0
	if len(solved_captcha) != len(captcha[:-4]): # If length of recognition is wrong, don't count it to avoid offsetting of letters
		return -1
	for i, letter in enumerate(captcha[:-4]):
		try:
			if letter == solved_captcha[i]:
				score += 1
		except:
			continue
	return score

def run_letter_mode(letters_dir, captcha_path): # solve in letter by letter mode
	split_letters(captcha_path)
	solved_captcha = recognize_captcha_letters(letters_dir)
	print("Guessed: " + solved_captcha)
	score = validate_letters(solved_captcha, captcha_path.split('/')[1])
	return score

def benchmark_letter_mode(): # run benchamrk for letter by letter mode
	scores = []
	final_score = 0
	for captcha in os.listdir('solved_captchas'):
		print('Running letter mode on {}'.format(captcha))
		treated_captcha_path = treat_captcha(os.path.join('solved_captchas', captcha))
		score = run_letter_mode('split_letters', treated_captcha_path)
		if score != -1:
			scores.append(score)
	for score in scores:
		final_score += score
	total_score = final_score
	final_score /= len(scores)
	max_score = len(scores) * 12
	print('Benchmark ran on {} captchas'.format(len(scores)))
	print('Good: {}\nBad: {}\nScore: {}%'.format(total_score, max_score - total_score, (100 * final_score) / 12))
	exit()

def split_letters(filename): # needs optimization, there is some leftover noise in some letters
	letters_dir = 'split_letters'

	gray = cv2.imread(filename, 0)
	# Add some extra padding around the image
	gray = cv2.copyMakeBorder(gray, 8, 8, 8, 8, cv2.BORDER_REPLICATE)
	# threshold the image (convert it to pure black and white)
	thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
	# find the contours (continuous blobs of pixels) the image
	contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
	letter_image_regions = []
	# Now we can loop through each of the four contours and extract the letter inside of each one
	for contour in contours:
		# Get the rectangle that contains the contour
		(x, y, w, h) = cv2.boundingRect(contour)
		letter_image_regions.append((x, y, w, h))

		letter_image_regions = sorted(letter_image_regions, key=lambda x: x[0])

	if len(letter_image_regions) > 12: # If true, there is a i or j in the text (we have 12 char captchas)
		for i, l in enumerate(letter_image_regions):
			if l[2] <= 4 and l[3] <= 4: # if current region width is equal to height, then it's the dot of i or j
				letter_image_regions.remove(l) # remove region for the i or j dot
				letter_image_regions[i-1] = (letter_image_regions[i-1][0], letter_image_regions[i-1][1] - 5, letter_image_regions[i-1][2], letter_image_regions[i-1][3] + 5) # extend region of i and j body

	if len(letter_image_regions) > 13: # If too much letters, we have a letter parsing error
		print('Too much letters detected, not saving to avoid corruption of dataset')
		return

	# Save split letters on disk
	nb = 0 # Iterator for letter number
	for letter_bounding_box in letter_image_regions:
		x, y, w, h = letter_bounding_box
		letter_image = gray[y - 2:y + h + 2, x - 2:x + w + 2]
		# Add white border to letters for tesseract optimization
		bordered_img = cv2.copyMakeBorder(letter_image, 8, 8, 8, 8, cv2.BORDER_CONSTANT, value=[255, 255, 255])
		if not os.path.exists(letters_dir):
				os.makedirs(letters_dir)
		cv2.imwrite(letters_dir + '/{}.png'.format(nb), bordered_img)
		nb += 1