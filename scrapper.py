import selenium
import time
import csv
from datetime import date
from array import *
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


class entry:
    def __init__(self, date: str, description: str, value: float):
        self.date = date
        self.description = description
        self.value = value


def export_to_file(in_array):
    entries_array = convert_to_entries(in_array)

    with open('extract.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        for entry in entries_array:
            writer.writerow([entry.date, entry.description, entry.value])


def convert_to_entries(in_array):
    entries: entry = []
    index = 0

    for array_entry in in_array:

        if ("€" in array_entry) and ("," in array_entry):
            # if it's in the 3rd column - credit
            if index % 2 == 0:
                value = float(array_entry.strip("€ \t").replace(',', '.'))
                entries.append(
                    entry(in_array[index-2], in_array[index-1], value))
            # if it's in the 3rd column - debit
            elif index % 3 == 0:
                value = float(array_entry.strip("€ \t").replace(',', '.'))
                value = value * -1
                entries.append(
                    entry(in_array[index-3], in_array[index-2], value))

        index = index + 1

    return entries


def write_password(_driver: webdriver, _cardnumber: int):
    password = _cardnumber % 10000000

    # activates password field
    _driver.find_element(
        By.XPATH, "/html/body/div[2]/div/div/div[1]/form/div/div[1]/div[3]/div[1]/input").click()
    time.sleep(0.5)

    # finds the lines for password input
    line1_element = _driver.find_element(
        By.XPATH, "/html/body/div[2]/div/div/div[1]/form/div/div[1]/div[4]/table/tbody/tr[2]")
    line2_element = _driver.find_element(
        By.XPATH, "/html/body/div[2]/div/div/div[1]/form/div/div[1]/div[4]/table/tbody/tr[3]")

    # input
    for digit in iter(str(password)):

        try:
            element = line1_element.find_element(
                By.XPATH, ".//*[contains(text(), '{}')]".format(digit))

        except NoSuchElementException:
            pass

        else:
            time.sleep(0.2)
            element.click()
            continue

        try:
            element = line2_element.find_element(
                By.XPATH, ".//*[contains(text(), '{}')]".format(digit))

        except NoSuchElementException:
            pass

        else:
            time.sleep(0.5)
            element.click()
            continue


def set_date(_driver: webdriver):
    action = ActionChains(_driver)
    today = date.today()
    field_size = 3

    # date select
    select = Select(_driver.find_element(By.ID, 'selectIntervalTime'))
    select.select_by_index(4)
    time.sleep(2)

    # start date
    input_element = _driver.find_element(
        By.XPATH, "/html/body/div[2]/div[4]/div[2]/div/div[1]/div/input[1]")
    input_element.click()
    action.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(
        Keys.SHIFT).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT)
    action.perform()

    # fills day, month and year with 1
    while field_size > 0:
        input_element.send_keys(1)
        action.send_keys(Keys.TAB)
        action.perform()
        field_size = field_size - 1

    # end date - today
    input_element = _driver.find_element(
        By.XPATH, "/html/body/div[2]/div[4]/div[2]/div/div[1]/div/input[2]")
    input_element.click()
    action.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(
        Keys.SHIFT).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT)
    action.perform()

    input_element.send_keys(today.strftime("%d"))
    input_element.send_keys(today.strftime("%m"))
    input_element.send_keys(today.strftime("%Y"))


def read_cardnumber():
    f = open("cartao.txt", "r")
    _cardnumber = int(f.readline())

    return _cardnumber


# main
def main():

    cardnumber = read_cardnumber()

    driver = webdriver.Chrome()
    driver.maximize_window()

    driver.get("https://hbcartaoticket.unicre.pt")

    # inserts card number
    driver.find_element(
        By.XPATH, "/html/body/div[2]/div/div/div[1]/form/div/div[1]/div[2]/div/input").send_keys(cardnumber)

    write_password(driver, cardnumber)

    # Entrar button
    input_element = driver.find_element(
        By.XPATH, "/html/body/div[2]/div/div/div[2]/div/input")
    input_element.click()
    time.sleep(0.5)

    # Ver Movimentos button
    input_element = driver.find_element(
        By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div/div[3]/div/a/input")
    input_element.click()

    set_date(driver)

    # Aplicar button
    input_element = driver.find_element(
        By.XPATH, "/html/body/div[2]/div[4]/div[2]/div/div[2]/input")
    input_element.click()
    time.sleep(2)

    # finds table
    table_element = driver.find_element(By.XPATH, "/html/body/div[2]/div[8]")

    # separates the table's rows
    rows = table_element.find_elements(
        By.XPATH, "./div[@class = 'row table-content']")

    # array to store all table values
    values_aux = []

    for row in rows:

        fields = row.find_elements(By.XPATH, "./div")

        for field in fields:
            value_aux = field.find_element(By.XPATH, "./label").text
            values_aux.append(value_aux)

    driver.quit()
    export_to_file(values_aux)


if __name__ == "__main__":
    main()
