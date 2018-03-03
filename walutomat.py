from bs4 import BeautifulSoup
from selenium import webdriver
import requests, time, sys
#from selenium.webdriver.common.keys import Keys
# from selenium.webdriver import ActionChains

#TODO: Headless mode has a problem with finding elements
# headless
'''options = webdriver.ChromeOptions()
options.add_argument('headless')
webdriver = webdriver.Chrome(chrome_options=options)'''
# normal browser
webdriver = webdriver.Chrome()

transaction_type = sys.argv[1]
wanted_amount = sys.argv[2]
wanted_currency = sys.argv[3]

# print(transaction_type, wanted_amount, wanted_currency)


def rate_walutomat(transaction_type, currency):     #finds exchange rate which will be first in an offer list
    if transaction_type == 'buy':
        currency_exchange = 'PLN_{}'.format(currency)
    else:
        currency_exchange = '{}_PLN'.format(currency)
    offer_url = 'https://stary.walutomat.pl/wymiana-walut.php?curr={}'.format(currency_exchange)
    request = requests.get(offer_url)
    content = request.content
    soup = BeautifulSoup(content, 'html.parser')
    offers_rate = soup.select('table[id={}] td[class="center"]'.format(currency_exchange))
    offers_amount = soup.select('table[id={}] td[width="110"]'.format(currency_exchange))
    total, i= 0, 0
    #TODO total is set to reach 1500, it is good value only for offers in PLN, need to add options for other currencies
    while total < 1500:
        sum = offers_amount[i]
        sum = sum.getText()[:-4].replace(',', '.')
        total = total + float(sum.replace(' ', ''))
        i = i + 1

    if transaction_type == 'buy':
        exchange_rate = float(offers_rate[i-1].getText()) + 0.0001
    else:
        exchange_rate = float(offers_rate[i-1].getText()) - 0.0001
    return(exchange_rate)

def exchange_walutomat(username, password, transaction_type, first_currency, second_currency, amount, rate):
    webdriver.implicitly_wait(10)
    webdriver.get('https://panel.walutomat.pl/moj-walutomat')
    webdriver.find_element_by_id('username').send_keys(username)
    webdriver.find_element_by_id('password').send_keys(password)
    webdriver.find_element_by_class_name('bem-button__inner-text').click()
    time.sleep(5)
    webdriver.get('https://user.walutomat.pl/#/order-placement')
    element = webdriver.find_element_by_id('order-volume')
    element.clear()
    element.send_keys(str(amount))     #send amount
    time.sleep(3)


    #TODO: choose transaction type from a dropdown menu. Buy is by default.
    '''            
    webdriver.find_element_by_id('order-type').click()       #click on buy/sell
    time.sleep(2)
    
    # element from a dropdown menu is wrongly selected. To be fixed 
    if transaction_type == 'buy':       #choose buy/sell
        webdriver.find_element_by_class_name('select2-results__option select2-results__option--highlighted')
    elif transaction_type == 'sell':
        webdriver.find_element_by_link_text('Chcę sprzedać')
    '''

    #TODO: find a way to select element for a different currencies. USD/PLN is by default.
    # element selector from a dropdown menu doesn't work
    '''
    element.send_keys(Keys.TAB, Keys.SPACE)      #click to choose first currency
    time.sleep(2)
    webdriver.find_element_by_class_name('icon-{}'.format(first_currency)).click()        #choose first currency
    time.sleep(2)
    webdriver.send_keys(Keys.TAB)      #click on second currency
    time.sleep(2)
    webdriver.send_keys(Keys.SPACE)
    webdriver.find_element_by_class_name('icon-{}'.format(second_currency)).click()     #choose second currency
    time.sleep(2)
    webdriver.find_element_by_id('price-type-fixed').click()       #choose custom exchange rate
    time.sleep(2)
    '''

    webdriver.find_element_by_id('order-at-price').send_keys(str(rate))     #send custom exchange rate
    time.sleep(3)
    webdriver.find_element_by_id('order-preliminary-submit').click()        #confirm transaction parameters
    time.sleep(3)
    element = webdriver.find_elements_by_class_name('content')
    podsumowanie = element[3].text.split('\n')
    podsumowanie = '{}, kurs {} {}\n{}\n'.format(' '.join(podsumowanie[1:3]), podsumowanie[4].lower(), podsumowanie[5], ' '.join(podsumowanie[6:8]))
    print(podsumowanie)
    confirmation = input('Czy potwierdzasz?')
    if confirmation in ['T', 't', 'Tak', 'tak', 'Y', 'y', 'Yes', 'yes']:
        try:
            webdriver.find_element_by_id('confirm-exchange').click()
            print('Zlecenie zostało złożone.')
        except:
            'Something goes wrong. Laaambaada!'
    else:
        print('Operacja anulowana.')
    webdriver.close()
    return

rate = round(rate_walutomat(transaction_type, wanted_currency), 4)
#rate = 3.41 # fixed rate for tests

username = input('Username: ')
password = input('Password: ')
exchange_walutomat(username, password, transaction_type, wanted_currency, 'PLN', wanted_amount, rate)        #transaction type, 1st and 2nd currency aren't used now. TODO
