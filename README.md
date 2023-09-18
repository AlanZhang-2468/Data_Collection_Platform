# Data Collection Platform

A website used to collect annotated chemical reaction procedure data

URL: http://101.42.25.173:443

## Installation

Clone:
```
$ git clone https://github.com/AlanZhang-2468/Data_Collection_Platform
$ cd Data_Collection_Platform
```
Create & active virtual enviroment then install dependencies:
```
$ python3 -m venv env  # use `python ...` on Windows
$ source env/bin/activate  # use `env\Scripts\activate` on Windows
(env) $ pip install -r requirements.txt
```

Initialize the database
```
(env) $ flask initdb
```
Then run the website in the local laptop:
```
(env) $ flask run
* Running on http://127.0.0.1:5000/
```
If you want run the website in a certain URL, then input the following command line to run the website:
```
(env) $ flask run --host=your_host_address --port=your_port_address
* Replace your_host_address and your_port_address with real address.
```
