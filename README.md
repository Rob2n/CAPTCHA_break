# CAPTCHA_break

A Python3 CAPTCHA solving bot based on Tesseract OCR

![Image](./examples/bItgna7sgbEc.png "Example CAPTCHA")
![Image](examples/KfC2ppLzP4Dz.png "Example CAPTCHA")
![Image](examples/xGV6TrLTaHf4.png "Example CAPTCHA")


## Install

You need :

- Python3 and pip
- Install the required pip modules as such :
	+ `pip3 install -r requirements.txt`

## Usage
```
usage: captcha_break.py [-h] [-b] [-s SAVE] [-o]

optional arguments:
  -h, --help            show this help message and exit
  -b, --benchmark       make a benchmark on 100 recognitions
  -s SAVE, --save SAVE  save <SAVE> captchas to disk (for ML dataset, offline demo solving, etc)
  -o, --offline         solve offline CAPTCHAs located in offline_captchas folder
```
**captcha_break** relies on the site [root-me.org](https://root-me.org) in order to get the CAPTCHAs and automatically verify it's results so you will have to create an account/log in to the site in order to do online solving.

### Online

When doing online solving (connected to [root-me.org](https://root-me.org)) you can use the following options :

- `./captcha_break` : Send a single solve request to [root-me.org](https://root-me.org) and display the results
- `./captcha_break --benchmark` : Send 100 solve requests to [root-me.org](https://root-me.org) and calculate a percentage of success based on the results
- `./captcha_break --save SAVE` : Save *\<SAVE\>* number of CAPTCHAs to disk (for ML dataset, offline demo solving, etc)

### Offline

**captcha_break** can also do offline solves of local CAPTCHAs by using the following option :

- `./captcha_break --offline` : Will solve all CAPTCHA images located in *offline_captchas* folder and display the results

## FAQ

#### I get an error when runnig `./captcha_break.py`

If you get this error message when running the program :

```
Error when connecting to https://root-me.org website.
Are you logged into the site ?
```
You need to go on [root-me.org](https://root-me.org) and create an account/log in.
Once you are logged-in, the bot is able to connect to the site and retrieve new CAPTCHAs.