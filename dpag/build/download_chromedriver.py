from webdriver_manager.chrome import ChromeDriverManager

ChromeDriverManager(path="/usr/bin", version="114.0.5735.90").install()
print('ChromeDriver download was successful.')