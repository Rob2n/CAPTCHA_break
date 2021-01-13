#! /usr/bin/env python3

import os
import cv2

def save_valid_captcha(solve): # save solved captcha to disk
	if not os.path.exists('solved_captchas'):
		os.makedirs('solved_captchas')
	filename = "solved_captchas/{}.png".format(solve)
	img = cv2.imread('captcha_untreated.png')
	cv2.imwrite(filename, img)
