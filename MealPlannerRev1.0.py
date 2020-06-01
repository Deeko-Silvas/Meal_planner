from MainWindow import Ui_mainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import sys

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
import re
import sqlite3
import pyperclip
from math import ceil

categories_food = ["Breakfast", "Meat", "Fish", "Ready Meal", "Dairy", "Sides", "Fruit", "Veg", "Sweet Snack", "Savoury Snack",
                   "Seasoning", "Drink", "Other"]
categories_all_food = ["All", "Breakfast", "Meat", "Fish", "Ready Meal", "Dairy", "Sides", "Fruit", "Veg", "Sweet Snack",
                       "Savoury Snack", "Seasoning", "Drink", "Other", "Deleted"]
categories_food_del = ["All", "Breakfast", "Meat", "Fish", "Dairy", "Ready Meal", "Sides", "Fruit", "Veg", "Sweet Snack",
                       "Savoury Snack", "Seasoning", "Drink", "Other", "Deleted"]
categories_all = ["All", "Recipe", "Breakfast", "Meat", "Fish", "Dairy", "Ready Meal", "Sides", "Fruit", "Veg", "Sweet Snack",
                  "Savoury Snack", "Seasoning", "Drink", "Other"]
day_list = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
meal_list = ["breakfast", "snack1", "lunch", "snack2", "dinner", "snack3"]

dictionary_food = {"Breakfast":7, "Meat":3, "Fish":4, "Ready Meal":5, "Dairy":12, "Sides":12, "Fruit":1, "Veg":1, "Sweet Snack":8, "Savoury Snack":9,
                   "Seasoning":6, "Drink":10, "Other":11, "Recipe":25}
exersize_list = ["1-3 Hours", "4-6 Hours", "6+ Hours"]

count = 0

file_name_store = ""
meal_id = None

class MainWindow(QtWidgets.QMainWindow, Ui_mainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.katch_radio.toggled.connect(self.km)
        self.harris_radio.toggled.connect(self.hb)
        self.age_entry.setDisabled(True)
        self.height_entry.setDisabled(True)
        self.exersize_combo.addItems(exersize_list)

        self.calorie_calculate_button.clicked.connect(self.calculate_calorie_allowance)

        self.actionSave_As.triggered.connect(self.file_save_as)
        self.actionOpen.triggered.connect(self.file_open)
        self.actionNEw.triggered.connect(self.new)
        self.actionSave.triggered.connect(self.file_save)
        self.actionExit.triggered.connect(self.exit)


        self.add_food_category_combo.addItems(categories_food)
        self.edit_food_category_combo.addItems(categories_food_del)
        self.add_meal_category_combo.addItems(categories_all_food)
        self.meal_planner_category_combo.addItems(categories_all)
        self.edit_meal_category_combo.addItems(categories_all_food)

        self.add_food_url_search_button.clicked.connect(self.get_tesco_data)
        self.add_food_add_button.clicked.connect(self.add_new_food)
        self.edit_food_url_search_button.clicked.connect(self.search_edit_food)
        self.edit_food_save_button.clicked.connect(self.edit_food_save)
        self.add_meal_url_search_button.clicked.connect(lambda: self.search_food_meal(self.add_meal_url_search_entry,
                                                                                      self.add_meal_search_table,
                                                                                      self.add_meal_category_combo))
        self.add_meal_select_button.clicked.connect(lambda: self.add_ingredient(self.add_meal_recipe_table,
                                                                                self.add_meal_search_table,
                                                                                self.add_meal_calculate,
                                                                                self.add_meal_carbs_entry,
                                                                                self.add_meal_protein_entry,
                                                                                self.add_meal_fat_entry,
                                                                                self.add_meal_sugar_entry,
                                                                                self.add_meal_calories_entry,
                                                                                self.add_meal_servings_entry))
        self.add_meal_delete_button.clicked.connect(lambda: self.meal_delete_ingredient(self.add_meal_recipe_table,
                                                                                        self.add_meal_calculate,
                                                                                        self.add_meal_carbs_entry,
                                                                                        self.add_meal_protein_entry,
                                                                                        self.add_meal_fat_entry,
                                                                                        self.add_meal_sugar_entry,
                                                                                        self.add_meal_calories_entry,
                                                                                        self.add_meal_servings_entry))
        self.add_meal_add_button.clicked.connect(lambda: self.add_meal_todb(self.add_meal_recipe_table,
                                                                            self.add_meal_name_entry,
                                                                            self.add_meal_recipe_book_entry,
                                                                            self.add_meal_page_entry,
                                                                            self.add_meal_carbs_entry,
                                                                            self.add_meal_protein_entry,
                                                                            self.add_meal_fat_entry,
                                                                            self.add_meal_sugar_entry,
                                                                            self.add_meal_calories_entry,
                                                                            self.add_meal_servings_entry))
        self.edit_meal_search_button.clicked.connect(self.search_edit_meal)
        self.edit_meal_select_button.clicked.connect(lambda: self.add_ingredient(self.edit_meal_recipe_table,
                                                                                 self.edit_meal_search_table,
                                                                                 self.add_meal_calculate,
                                                                                 self.edit_meal_carbs_entry,
                                                                                 self.edit_meal_protein_entry,
                                                                                 self.edit_meal_fat_entry,
                                                                                 self.edit_meal_sugar_entry,
                                                                                 self.edit_meal_calories_entry,
                                                                                 self.edit_meal_servings_entry))
        self.edit_meal_choose_button.clicked.connect(self.edit_meal_choose)
        self.edit_meal_url_search_button.clicked.connect(lambda: self.search_food_meal(self.edit_meal_url_search_entry,
                                                                                       self.edit_meal_search_table,
                                                                                       self.edit_meal_category_combo))
        self.edit_meal_delete_button.clicked.connect(lambda: self.meal_delete_ingredient(self.edit_meal_recipe_table,
                                                                                         self.add_meal_calculate,
                                                                                         self.edit_meal_carbs_entry,
                                                                                         self.edit_meal_protein_entry,
                                                                                         self.edit_meal_fat_entry,
                                                                                         self.edit_meal_sugar_entry,
                                                                                         self.edit_meal_calories_entry,
                                                                                         self.edit_meal_servings_entry))
        self.edit_meal_add_button.clicked.connect(lambda: self.add_meal_todb(self.edit_meal_recipe_table,
                                                                            self.edit_meal_name_entry,
                                                                            self.edit_meal_recipe_book_entry,
                                                                            self.edit_meal_page_entry,
                                                                            self.edit_meal_carbs_entry,
                                                                            self.edit_meal_protein_entry,
                                                                            self.edit_meal_fat_entry,
                                                                            self.edit_meal_sugar_entry,
                                                                            self.edit_meal_calories_entry,
                                                                            self.edit_meal_servings_entry))
        self.edit_food_delete_button.clicked.connect(self.edit_food_delete)

        # Copy Day buttons

        self.phil_monday_copy_button.clicked.connect(lambda: self.copy_day1("monday", "phil"))
        self.phil_monday_paste_button.clicked.connect(lambda: self.paste_day1("monday", "phil"))
        self.phil_tuesday_copy_button.clicked.connect(lambda: self.copy_day1("tuesday", "phil"))
        self.phil_tuesday_paste_button.clicked.connect(lambda: self.paste_day1("tuesday", "phil"))
        self.phil_wednesday_copy_button.clicked.connect(lambda: self.copy_day1("wednesday", "phil"))
        self.phil_wednesday_paste_button.clicked.connect(lambda: self.paste_day1("wednesday", "phil"))
        self.phil_thursday_copy_button.clicked.connect(lambda: self.copy_day1("thursday", "phil"))
        self.phil_thursday_paste_button.clicked.connect(lambda: self.paste_day1("thursday", "phil"))
        self.phil_friday_copy_button.clicked.connect(lambda: self.copy_day1("friday", "phil"))
        self.phil_friday_paste_button.clicked.connect(lambda: self.paste_day1("friday", "phil"))
        self.phil_saturday_copy_button.clicked.connect(lambda: self.copy_day1("saturdady", "phil"))
        self.phil_saturday_paste_button.clicked.connect(lambda: self.paste_day1("saturday", "phil"))
        self.phil_sunday_copy_button.clicked.connect(lambda: self.copy_day1("sunday", "phil"))
        self.phil_sunday_paste_button.clicked.connect(lambda: self.paste_day1("sunday", "phil"))

        self.vikki_monday_copy_button.clicked.connect(lambda: self.copy_day1("monday", "vikki"))
        self.vikki_monday_paste_button.clicked.connect(lambda: self.paste_day1("monday", "vikki"))
        self.vikki_tuesday_copy_button.clicked.connect(lambda: self.copy_day1("tuesday", "vikki"))
        self.vikki_tuesday_paste_button.clicked.connect(lambda: self.paste_day1("tuesday", "vikki"))
        self.vikki_wednesday_copy_button.clicked.connect(lambda: self.copy_day1("wednesday", "vikki"))
        self.vikki_wednesday_paste_button.clicked.connect(lambda: self.paste_day1("wednesday", "vikki"))
        self.vikki_thursday_copy_button.clicked.connect(lambda: self.copy_day1("thursday", "vikki"))
        self.vikki_thursday_paste_button.clicked.connect(lambda: self.paste_day1("thursday", "vikki"))
        self.vikki_friday_copy_button.clicked.connect(lambda: self.copy_day1("friday", "vikki"))
        self.vikki_friday_paste_button.clicked.connect(lambda: self.paste_day1("friday", "vikki"))
        self.vikki_saturday_copy_button.clicked.connect(lambda: self.copy_day1("saturdady", "vikki"))
        self.vikki_saturday_paste_button.clicked.connect(lambda: self.paste_day1("saturday", "vikki"))
        self.vikki_sunday_copy_button.clicked.connect(lambda: self.copy_day1("sunday", "vikki"))
        self.vikki_sunday_paste_button.clicked.connect(lambda: self.paste_day1("sunday", "vikki"))

        self.phil_copy_to_vikki_button.clicked.connect(lambda: self.copy_week("phil", "vikki"))
        self.vikki_copy_to_phil_button.clicked.connect(lambda: self.copy_week("vikki", "phil"))

        # self.edit_meal_save_button.clicked.connect(mainWindow.edit_meal_save)

        self.meal_planner_search_button.clicked.connect(
            lambda: self.search_food_meal(self.meal_planner_url_search_entry,
                                          self.meal_planner_search_table,
                                          self.meal_planner_category_combo))

        self.edit_food_table.setColumnWidth(0, 20)
        self.edit_food_table.setColumnWidth(13, 20)

        # Meal planner column widths

        add_meal_recipe_column_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        add_meal_recipe_column_width_list = [0, 0, 500, 0, 0, 0, 0, 80, 80, 80, 80, 100, 150, 0, 0, 0, 0, 0]
        #add_meal_recipe_column_width_list = [50, 50, 500, 50, 50, 50, 50, 80, 80, 80, 80, 100, 150, 50, 50, 50, 50, 50]

        for add_meal_recipe_col_int, add_meal_recipe_col_width in zip(add_meal_recipe_column_list,
                                                                      add_meal_recipe_column_width_list):
            self.add_meal_recipe_table.setColumnWidth(add_meal_recipe_col_int, add_meal_recipe_col_width)
            self.edit_meal_recipe_table.setColumnWidth(add_meal_recipe_col_int, add_meal_recipe_col_width)

        add_meal_search_column_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, ]
        add_meal_search_column_width_list = [0, 100, 390, 0, 100, 70, 70, 70, 70, 70, 70, 90, 140, 0, 0, 0]

        for add_meal_search_col_int, add_meal_search_col_width in zip(add_meal_search_column_list,
                                                                      add_meal_search_column_width_list):
            self.add_meal_search_table.setColumnWidth(add_meal_search_col_int, add_meal_search_col_width)
            self.edit_meal_search_table.setColumnWidth(add_meal_search_col_int, add_meal_search_col_width)
            self.meal_planner_search_table.setColumnWidth(add_meal_search_col_int, add_meal_search_col_width)

        edit_food_column_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        edit_food_column_width_list = [0, 130, 370, 200, 80, 48, 48, 48, 48, 48, 50, 72, 92, 0, 72]

        for edit_food_col_int, edit_food_col_width in zip(edit_food_column_list, edit_food_column_width_list):
            self.edit_food_table.setColumnWidth(edit_food_col_int, edit_food_col_width)

        edit_meal_column_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        edit_meal_column_width_list = [0, 300, 300, 0, 100, 70, 70, 70, 0, 70]

        for edit_meal_col_int, edit_meal_col_width in zip(edit_meal_column_list, edit_meal_column_width_list):
            self.edit_meal_table.setColumnWidth(edit_meal_col_int, edit_meal_col_width)

        shopping_list_column_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        shopping_list_column_width_list = [0, 100, 400, 430, 100, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 0, 80, 100, 0]
        #shopping_list_column_width_list = [100, 100, 400, 430, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
                                           #100, 80, 80, 100]

        column_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        column_width_list = [0, 0, 180, 0, 0, 0, 0, 0, 0, 0, 0, 50, 50, 0, 0]
        #column_width_list = [50, 50, 180, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]

        for shopping_list_col_int, shopping_list_col_width in zip(shopping_list_column_list,
                                                                  shopping_list_column_width_list):
            self.shopping_list_table.setColumnWidth(shopping_list_col_int, shopping_list_col_width)
            self.shopping_list_table_non_tesco.setColumnWidth(shopping_list_col_int, shopping_list_col_width)

        for widget in self.groupBox_11.children():
            if isinstance(widget, QtWidgets.QTableWidget):
                widget.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
                for column_int, column_width in zip(column_list, column_width_list):
                    widget.setColumnWidth(column_int, column_width)

        for widget in self.groupBox_12.children():
            if isinstance(widget, QtWidgets.QTableWidget):
                widget.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
                for column_int, column_width in zip(column_list, column_width_list):
                    widget.setColumnWidth(column_int, column_width)

        # meal add, delete, copy, paste buttons

        for button in self.groupBox_11.children():
            if isinstance(button, QtWidgets.QPushButton) and "add" in button.objectName():
                button.released.connect(lambda: self.add_button(self.scrollAreaWidgetContents_4.sender()))


        for button in self.groupBox_12.children():
            if isinstance(button, QtWidgets.QPushButton) and "add" in button.objectName():
                button.released.connect(lambda: self.add_button(self.scrollAreaWidgetContents_7.sender()))

        for button in self.groupBox_11.children():
            if isinstance(button, QtWidgets.QPushButton) and "delete" in button.objectName():
                button.released.connect(lambda: self.delete_button(self.scrollAreaWidgetContents_4.sender()))

        for button in self.groupBox_12.children():
            if isinstance(button, QtWidgets.QPushButton) and "delete" in button.objectName():
                button.released.connect(lambda: self.delete_button(self.scrollAreaWidgetContents_7.sender()))

        for button in self.groupBox_11.children():
            if isinstance(button, QtWidgets.QPushButton) and "copy" in button.objectName():
                button_split = button.objectName().split("_")
                if button_split[2] in meal_list:
                    button.released.connect(lambda: self.copy_button(self.scrollAreaWidgetContents_4.sender()))

        for button in self.groupBox_12.children():
            if isinstance(button, QtWidgets.QPushButton) and "copy" in button.objectName():
                button_split = button.objectName().split("_")
                if button_split[2] in meal_list:
                    button.released.connect(lambda: self.copy_button(self.scrollAreaWidgetContents_7.sender()))

        for button in self.groupBox_11.children():
            if isinstance(button, QtWidgets.QPushButton) and "paste" in button.objectName():
                button_split = button.objectName().split("_")
                if button_split[2] in meal_list:
                    button.released.connect(lambda: self.paste_button(self.scrollAreaWidgetContents_4.sender()))

        for button in self.groupBox_12.children():
            if isinstance(button, QtWidgets.QPushButton) and "paste" in button.objectName():
                button_split = button.objectName().split("_")
                if button_split[2] in meal_list:
                    button.released.connect(lambda: self.paste_button(self.scrollAreaWidgetContents_7.sender()))

        # Clear buttons

        self.phil_clear_week_button.clicked.connect(lambda: self.clear_week("phil"))
        self.vikki_clear_week_button.clicked.connect(lambda: self.clear_week("vikki"))

        self.phil_clear_monday_button.clicked.connect(lambda: self.clear_day("phil", "monday"))
        self.phil_clear_tuesday_button.clicked.connect(lambda: self.clear_day("phil", "tuesday"))
        self.phil_clear_wednesday_button.clicked.connect(lambda: self.clear_day("phil", "wednesday"))
        self.phil_clear_thursday_button.clicked.connect(lambda: self.clear_day("phil", "thursday"))
        self.phil_clear_friday_button.clicked.connect(lambda: self.clear_day("phil", "friday"))
        self.phil_clear_saturday_button.clicked.connect(lambda: self.clear_day("phil", "saturday"))
        self.phil_clear_sunday_button.clicked.connect(lambda: self.clear_day("phil", "sunday"))

        self.vikki_clear_monday_button.clicked.connect(lambda: self.clear_day("vikki", "monday"))
        self.vikki_clear_tuesday_button.clicked.connect(lambda: self.clear_day("vikki", "tuesday"))
        self.vikki_clear_wednesday_button.clicked.connect(lambda: self.clear_day("vikki", "wednesday"))
        self.vikki_clear_thursday_button.clicked.connect(lambda: self.clear_day("vikki", "thursday"))
        self.vikki_clear_friday_button.clicked.connect(lambda: self.clear_day("vikki", "friday"))
        self.vikki_clear_saturday_button.clicked.connect(lambda: self.clear_day("vikki", "saturday"))
        self.vikki_clear_sunday_button.clicked.connect(lambda: self.clear_day("vikki", "sunday"))

        # Set macros to 0.0

        for entry in self.groupBox_11.children():
            if isinstance(entry, QtWidgets.QLineEdit):
                entry.setText("0.0")
        for entry in self.groupBox_12.children():
            if isinstance(entry, QtWidgets.QLineEdit):
                entry.setText("0.0")

        self.add_meal_recipe_table.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.edit_meal_recipe_table.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.edit_food_table.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)

        # Meal planner calulate macros

        self.phil_monday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_monday_breakfast_table,
                                                self.phil_monday_breakfast_table.currentRow(),
                                                self.phil_monday_breakfast_table.currentColumn()))
        self.phil_monday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_monday_snack1_table,
                                                self.phil_monday_snack1_table.currentRow(),
                                                self.phil_monday_snack1_table.currentColumn()))
        self.phil_monday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_monday_lunch_table,
                                                self.phil_monday_lunch_table.currentRow(),
                                                self.phil_monday_lunch_table.currentColumn()))
        self.phil_monday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_monday_snack2_table,
                                                self.phil_monday_snack2_table.currentRow(),
                                                self.phil_monday_snack2_table.currentColumn()))
        self.phil_monday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_monday_dinner_table,
                                                self.phil_monday_dinner_table.currentRow(),
                                                self.phil_monday_dinner_table.currentColumn()))
        self.phil_monday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_monday_snack3_table,
                                                self.phil_monday_snack3_table.currentRow(),
                                                self.phil_monday_snack3_table.currentColumn()))

        self.phil_tuesday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_tuesday_breakfast_table,
                                                self.phil_tuesday_breakfast_table.currentRow(),
                                                self.phil_tuesday_breakfast_table.currentColumn()))
        self.phil_tuesday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_tuesday_snack1_table,
                                                self.phil_tuesday_snack1_table.currentRow(),
                                                self.phil_tuesday_snack1_table.currentColumn()))
        self.phil_tuesday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_tuesday_lunch_table,
                                                self.phil_tuesday_lunch_table.currentRow(),
                                                self.phil_tuesday_lunch_table.currentColumn()))
        self.phil_tuesday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_tuesday_snack2_table,
                                                self.phil_tuesday_snack2_table.currentRow(),
                                                self.phil_tuesday_snack2_table.currentColumn()))
        self.phil_tuesday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_tuesday_dinner_table,
                                                self.phil_tuesday_dinner_table.currentRow(),
                                                self.phil_tuesday_dinner_table.currentColumn()))
        self.phil_tuesday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_tuesday_snack3_table,
                                                self.phil_tuesday_snack3_table.currentRow(),
                                                self.phil_tuesday_snack3_table.currentColumn()))

        self.phil_wednesday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_wednesday_breakfast_table,
                                                self.phil_wednesday_breakfast_table.currentRow(),
                                                self.phil_wednesday_breakfast_table.currentColumn()))
        self.phil_wednesday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_wednesday_snack1_table,
                                                self.phil_wednesday_snack1_table.currentRow(),
                                                self.phil_wednesday_snack1_table.currentColumn()))
        self.phil_wednesday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_wednesday_lunch_table,
                                                self.phil_wednesday_lunch_table.currentRow(),
                                                self.phil_wednesday_lunch_table.currentColumn()))
        self.phil_wednesday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_wednesday_snack2_table,
                                                self.phil_wednesday_snack2_table.currentRow(),
                                                self.phil_wednesday_snack2_table.currentColumn()))
        self.phil_wednesday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_wednesday_dinner_table,
                                                self.phil_wednesday_dinner_table.currentRow(),
                                                self.phil_wednesday_dinner_table.currentColumn()))
        self.phil_wednesday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_wednesday_snack3_table,
                                                self.phil_wednesday_snack3_table.currentRow(),
                                                self.phil_wednesday_snack3_table.currentColumn()))

        self.phil_thursday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_thursday_breakfast_table,
                                                self.phil_thursday_breakfast_table.currentRow(),
                                                self.phil_thursday_breakfast_table.currentColumn()))
        self.phil_thursday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_thursday_snack1_table,
                                                self.phil_thursday_snack1_table.currentRow(),
                                                self.phil_thursday_snack1_table.currentColumn()))
        self.phil_thursday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_thursday_lunch_table,
                                                self.phil_thursday_lunch_table.currentRow(),
                                                self.phil_thursday_lunch_table.currentColumn()))
        self.phil_thursday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_thursday_snack2_table,
                                                self.phil_thursday_snack2_table.currentRow(),
                                                self.phil_thursday_snack2_table.currentColumn()))
        self.phil_thursday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_thursday_dinner_table,
                                                self.phil_thursday_dinner_table.currentRow(),
                                                self.phil_thursday_dinner_table.currentColumn()))
        self.phil_thursday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_thursday_snack3_table,
                                                self.phil_thursday_snack3_table.currentRow(),
                                                self.phil_thursday_snack3_table.currentColumn()))

        self.phil_friday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_friday_breakfast_table,
                                                self.phil_friday_breakfast_table.currentRow(),
                                                self.phil_friday_breakfast_table.currentColumn()))
        self.phil_friday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_friday_snack1_table,
                                                self.phil_friday_snack1_table.currentRow(),
                                                self.phil_friday_snack1_table.currentColumn()))
        self.phil_friday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_friday_lunch_table,
                                                self.phil_friday_lunch_table.currentRow(),
                                                self.phil_friday_lunch_table.currentColumn()))
        self.phil_friday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_friday_snack2_table,
                                                self.phil_friday_snack2_table.currentRow(),
                                                self.phil_friday_snack2_table.currentColumn()))
        self.phil_friday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_friday_dinner_table,
                                                self.phil_friday_dinner_table.currentRow(),
                                                self.phil_friday_dinner_table.currentColumn()))
        self.phil_friday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_friday_snack3_table,
                                                self.phil_friday_snack3_table.currentRow(),
                                                self.phil_friday_snack3_table.currentColumn()))

        self.phil_saturday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_saturday_breakfast_table,
                                                self.phil_saturday_breakfast_table.currentRow(),
                                                self.phil_saturday_breakfast_table.currentColumn()))
        self.phil_saturday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_saturday_snack1_table,
                                                self.phil_saturday_snack1_table.currentRow(),
                                                self.phil_saturday_snack1_table.currentColumn()))
        self.phil_saturday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_saturday_lunch_table,
                                                self.phil_saturday_lunch_table.currentRow(),
                                                self.phil_saturday_lunch_table.currentColumn()))
        self.phil_saturday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_saturday_snack2_table,
                                                self.phil_saturday_snack2_table.currentRow(),
                                                self.phil_saturday_snack2_table.currentColumn()))
        self.phil_saturday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_saturday_dinner_table,
                                                self.phil_saturday_dinner_table.currentRow(),
                                                self.phil_saturday_dinner_table.currentColumn()))
        self.phil_saturday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_saturday_snack3_table,
                                                self.phil_saturday_snack3_table.currentRow(),
                                                self.phil_saturday_snack3_table.currentColumn()))

        self.phil_sunday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_sunday_breakfast_table,
                                                self.phil_sunday_breakfast_table.currentRow(),
                                                self.phil_sunday_breakfast_table.currentColumn()))
        self.phil_sunday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_sunday_snack1_table,
                                                self.phil_sunday_snack1_table.currentRow(),
                                                self.phil_sunday_snack1_table.currentColumn()))
        self.phil_sunday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_sunday_lunch_table,
                                                self.phil_sunday_lunch_table.currentRow(),
                                                self.phil_sunday_lunch_table.currentColumn()))
        self.phil_sunday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_sunday_snack2_table,
                                                self.phil_sunday_snack2_table.currentRow(),
                                                self.phil_sunday_snack2_table.currentColumn()))
        self.phil_sunday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_sunday_dinner_table,
                                                self.phil_sunday_dinner_table.currentRow(),
                                                self.phil_sunday_dinner_table.currentColumn()))
        self.phil_sunday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.phil_sunday_snack3_table,
                                                self.phil_sunday_snack3_table.currentRow(),
                                                self.phil_sunday_snack3_table.currentColumn()))

        self.vikki_monday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_monday_breakfast_table,
                                                self.vikki_monday_breakfast_table.currentRow(),
                                                self.vikki_monday_breakfast_table.currentColumn()))
        self.vikki_monday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_monday_snack1_table,
                                                self.vikki_monday_snack1_table.currentRow(),
                                                self.vikki_monday_snack1_table.currentColumn()))
        self.vikki_monday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_monday_lunch_table,
                                                self.vikki_monday_lunch_table.currentRow(),
                                                self.vikki_monday_lunch_table.currentColumn()))
        self.vikki_monday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_monday_snack2_table,
                                                self.vikki_monday_snack2_table.currentRow(),
                                                self.vikki_monday_snack2_table.currentColumn()))
        self.vikki_monday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_monday_dinner_table,
                                                self.vikki_monday_dinner_table.currentRow(),
                                                self.vikki_monday_dinner_table.currentColumn()))
        self.vikki_monday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_monday_snack3_table,
                                                self.vikki_monday_snack3_table.currentRow(),
                                                self.vikki_monday_snack3_table.currentColumn()))

        self.vikki_tuesday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_tuesday_breakfast_table,
                                                self.vikki_tuesday_breakfast_table.currentRow(),
                                                self.vikki_tuesday_breakfast_table.currentColumn()))
        self.vikki_tuesday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_tuesday_snack1_table,
                                                self.vikki_tuesday_snack1_table.currentRow(),
                                                self.vikki_tuesday_snack1_table.currentColumn()))
        self.vikki_tuesday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_tuesday_lunch_table,
                                                self.vikki_tuesday_lunch_table.currentRow(),
                                                self.vikki_tuesday_lunch_table.currentColumn()))
        self.vikki_tuesday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_tuesday_snack2_table,
                                                self.vikki_tuesday_snack2_table.currentRow(),
                                                self.vikki_tuesday_snack2_table.currentColumn()))
        self.vikki_tuesday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_tuesday_dinner_table,
                                                self.vikki_tuesday_dinner_table.currentRow(),
                                                self.vikki_tuesday_dinner_table.currentColumn()))
        self.vikki_tuesday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_tuesday_snack3_table,
                                                self.vikki_tuesday_snack3_table.currentRow(),
                                                self.vikki_tuesday_snack3_table.currentColumn()))

        self.vikki_wednesday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_wednesday_breakfast_table,
                                                self.vikki_wednesday_breakfast_table.currentRow(),
                                                self.vikki_wednesday_breakfast_table.currentColumn()))
        self.vikki_wednesday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_wednesday_snack1_table,
                                                self.vikki_wednesday_snack1_table.currentRow(),
                                                self.vikki_wednesday_snack1_table.currentColumn()))
        self.vikki_wednesday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_wednesday_lunch_table,
                                                self.vikki_wednesday_lunch_table.currentRow(),
                                                self.vikki_wednesday_lunch_table.currentColumn()))
        self.vikki_wednesday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_wednesday_snack2_table,
                                                self.vikki_wednesday_snack2_table.currentRow(),
                                                self.vikki_wednesday_snack2_table.currentColumn()))
        self.vikki_wednesday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_wednesday_dinner_table,
                                                self.vikki_wednesday_dinner_table.currentRow(),
                                                self.vikki_wednesday_dinner_table.currentColumn()))
        self.vikki_wednesday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_wednesday_snack3_table,
                                                self.vikki_wednesday_snack3_table.currentRow(),
                                                self.vikki_wednesday_snack3_table.currentColumn()))

        self.vikki_thursday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_thursday_breakfast_table,
                                                self.vikki_thursday_breakfast_table.currentRow(),
                                                self.vikki_thursday_breakfast_table.currentColumn()))
        self.vikki_thursday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_thursday_snack1_table,
                                                self.vikki_thursday_snack1_table.currentRow(),
                                                self.vikki_thursday_snack1_table.currentColumn()))
        self.vikki_thursday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_thursday_lunch_table,
                                                self.vikki_thursday_lunch_table.currentRow(),
                                                self.vikki_thursday_lunch_table.currentColumn()))
        self.vikki_thursday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_thursday_snack2_table,
                                                self.vikki_thursday_snack2_table.currentRow(),
                                                self.vikki_thursday_snack2_table.currentColumn()))
        self.vikki_thursday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_thursday_dinner_table,
                                                self.vikki_thursday_dinner_table.currentRow(),
                                                self.vikki_thursday_dinner_table.currentColumn()))
        self.vikki_thursday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_thursday_snack3_table,
                                                self.vikki_thursday_snack3_table.currentRow(),
                                                self.vikki_thursday_snack3_table.currentColumn()))

        self.vikki_friday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_friday_breakfast_table,
                                                self.vikki_friday_breakfast_table.currentRow(),
                                                self.vikki_friday_breakfast_table.currentColumn()))
        self.vikki_friday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_friday_snack1_table,
                                                self.vikki_friday_snack1_table.currentRow(),
                                                self.vikki_friday_snack1_table.currentColumn()))
        self.vikki_friday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_friday_lunch_table,
                                                self.vikki_friday_lunch_table.currentRow(),
                                                self.vikki_friday_lunch_table.currentColumn()))
        self.vikki_friday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_friday_snack2_table,
                                                self.vikki_friday_snack2_table.currentRow(),
                                                self.vikki_friday_snack2_table.currentColumn()))
        self.vikki_friday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_friday_dinner_table,
                                                self.vikki_friday_dinner_table.currentRow(),
                                                self.vikki_friday_dinner_table.currentColumn()))
        self.vikki_friday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_friday_snack3_table,
                                                self.vikki_friday_snack3_table.currentRow(),
                                                self.vikki_friday_snack3_table.currentColumn()))

        self.vikki_saturday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_saturday_breakfast_table,
                                                self.vikki_saturday_breakfast_table.currentRow(),
                                                self.vikki_saturday_breakfast_table.currentColumn()))
        self.vikki_saturday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_saturday_snack1_table,
                                                self.vikki_saturday_snack1_table.currentRow(),
                                                self.vikki_saturday_snack1_table.currentColumn()))
        self.vikki_saturday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_saturday_lunch_table,
                                                self.vikki_saturday_lunch_table.currentRow(),
                                                self.vikki_saturday_lunch_table.currentColumn()))
        self.vikki_saturday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_saturday_snack2_table,
                                                self.vikki_saturday_snack2_table.currentRow(),
                                                self.vikki_saturday_snack2_table.currentColumn()))
        self.vikki_saturday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_saturday_dinner_table,
                                                self.vikki_saturday_dinner_table.currentRow(),
                                                self.vikki_saturday_dinner_table.currentColumn()))
        self.vikki_saturday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_saturday_snack3_table,
                                                self.vikki_saturday_snack3_table.currentRow(),
                                                self.vikki_saturday_snack3_table.currentColumn()))

        self.vikki_sunday_breakfast_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_sunday_breakfast_table,
                                                self.vikki_sunday_breakfast_table.currentRow(),
                                                self.vikki_sunday_breakfast_table.currentColumn()))
        self.vikki_sunday_snack1_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_sunday_snack1_table,
                                                self.vikki_sunday_snack1_table.currentRow(),
                                                self.vikki_sunday_snack1_table.currentColumn()))
        self.vikki_sunday_lunch_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_sunday_lunch_table,
                                                self.vikki_sunday_lunch_table.currentRow(),
                                                self.vikki_sunday_lunch_table.currentColumn()))
        self.vikki_sunday_snack2_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_sunday_snack2_table,
                                                self.vikki_sunday_snack2_table.currentRow(),
                                                self.vikki_sunday_snack2_table.currentColumn()))
        self.vikki_sunday_dinner_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_sunday_dinner_table,
                                                self.vikki_sunday_dinner_table.currentRow(),
                                                self.vikki_sunday_dinner_table.currentColumn()))
        self.vikki_sunday_snack3_table.cellChanged.connect(
            lambda: self.change_planner_portion(self.vikki_sunday_snack3_table,
                                                self.vikki_sunday_snack3_table.currentRow(),
                                                self.vikki_sunday_snack3_table.currentColumn()))

        self.add_meal_recipe_table.cellChanged.connect(
            lambda: self.change_meal_portion(self.add_meal_recipe_table,
                                             self.add_meal_recipe_table.currentRow(),
                                             self.add_meal_recipe_table.currentColumn()))
        self.edit_meal_recipe_table.cellChanged.connect(
            lambda: self.change_meal_portion(self.edit_meal_recipe_table,
                                             self.edit_meal_recipe_table.currentRow(),
                                             self.edit_meal_recipe_table.currentColumn()))
        self.add_meal_servings_entry.textChanged.connect(lambda: self.add_meal_calculate(self.add_meal_recipe_table,
                                                                                         self.add_meal_carbs_entry,
                                                                                         self.add_meal_protein_entry,
                                                                                         self.add_meal_fat_entry,
                                                                                         self.add_meal_sugar_entry,
                                                                                         self.add_meal_calories_entry,
                                                                                         self.add_meal_servings_entry))
        self.edit_meal_servings_entry.textChanged.connect(lambda: self.add_meal_calculate(self.edit_meal_recipe_table,
                                                                                          self.edit_meal_carbs_entry,
                                                                                          self.edit_meal_protein_entry,
                                                                                          self.edit_meal_fat_entry,
                                                                                          self.edit_meal_sugar_entry,
                                                                                          self.edit_meal_calories_entry,
                                                                                          self.edit_meal_servings_entry))

        self.tabs.currentChanged.connect(self.shopping_list_tab)
        self.shopping_list_calculate_price.clicked.connect(self.shopping_list_price)
        self.shopping_list_add_to_basket.clicked.connect(self.add_to_basket)



    def shopping_list_price(self):
        unable_to_find_list = []
        row_count = self.shopping_list_table.rowCount()
        calc_total_price = 0.0

        try:

            browser = webdriver.Chrome(
                executable_path="chromedriver.exe")
            row = 0
            while row < row_count:
                url = self.shopping_list_table.item(row, 3).text()
                browser.get(url)
                try:
                    price = float(browser.find_element_by_class_name("value").text)
                    self.shopping_list_table.setItem(row, 20, QtWidgets.QTableWidgetItem(f"£{price:.2f}"))
                    quantity = float(self.shopping_list_table.item(row, 18).text())
                    total_price = float(price) * int(quantity)
                    self.shopping_list_table.setItem(row, 21, QtWidgets.QTableWidgetItem(f"£{ total_price:.2f}"))
                    calc_total_price += total_price
                    row += 1
                except NoSuchElementException:
                    unable_to_find_list.append(self.shopping_list_table.item(row, 2).text())
                    self.cannotFind(row)
                    row_count -= 1
                except ValueError:
                    unable_to_find_list.append(self.shopping_list_table.item(row, 2).text())
                    self.cannotFind(row)
                    row_count -= 1


            browser.quit()
            if unable_to_find_list:
                self.message_box("Error", f"Unable to find the following products: {str(unable_to_find_list)[1:-1]}")
            self.totalPriceInput.setText(f"£{calc_total_price:.2f}")
        except NoSuchWindowException:
            return




        if unable_to_find_list:
            self.message_box("Error", f"Unable to find the following products: {str(unable_to_find_list)[1:-1]}")

    def add_to_basket(self):
        unable_to_find_list = []
        row_count = self.shopping_list_table.rowCount()
        try:
            browser = webdriver.Chrome(
                executable_path="chromedriver.exe")
            row = 0

            login_url = "https://secure.tesco.com/account/en-GB/login?from=/"
            browser.get(login_url)
            username_field = browser.find_element_by_id("username")
            username_field.send_keys("phil.livermore@zohomail.eu")
            password_field = browser.find_element_by_id("password")
            password_field.send_keys("Tesco1234")
            sign_in = browser.find_elements_by_class_name("ui-component__button")
            sign_in[1].click()
            basket_url = "https://www.tesco.com/groceries/en-GB/trolley"
            browser.get(basket_url)
            empty_basket_url = "https://www.tesco.com/groceries/en-GB/trolley?currentModal=emptyTrolley"
            browser.get(empty_basket_url)
            confirm = browser.find_element_by_class_name("js-empty-trolley-yes")
            confirm.click()
        except NoSuchWindowException:
            return

        while row < row_count:
            url = self.shopping_list_table.item(row, 3).text()
            browser.get(url)
            quantity = self.shopping_list_table.item(row, 18).text()
            try:
                input = browser.find_element_by_class_name("product-input")
                input.click()
                input.send_keys(Keys.BACK_SPACE)
                input.send_keys(quantity)

                add_button = browser.find_element_by_css_selector("button.small.add-control.button-secondary")
                add_button.click()
                row += 1

            except NoSuchElementException:
                unable_to_find_list.append(self.shopping_list_table.item(row, 2).text())
                self.cannotFind(row)
                row_count -= 1
            except ElementNotInteractableException:
                unable_to_find_list.append(self.shopping_list_table.item(row, 2).text())
                self.cannotFind(row)
                row_count -= 1



        if unable_to_find_list:
            self.message_box("Error", f"Unable to find the following products: {str(unable_to_find_list)[1:-1]}")

    def cannotFind(self, row):
        new_row = self.shopping_list_table_non_tesco.rowCount()
        self.shopping_list_table_non_tesco.insertRow(new_row)
        col = 0
        while col < 19:
            self.shopping_list_table_non_tesco.setItem(new_row, col, QtWidgets.QTableWidgetItem(
                self.shopping_list_table.item(row, col).text()))
            col += 1
        self.shopping_list_table.removeRow(row)


    def calculate_calorie_allowance(self):
        weight = self.weight_entry.text()
        body_fat = self.body_fat_entry.text()
        height = self.height_entry.text()
        age = self.age_entry.text()
        try:
            if self.katch_radio.isChecked():
                bmr = ceil(370 + (21.6 * (1 - (float(body_fat) / 100)) * float(weight)))
            elif self.katch_radio.isChecked() and self.female_radio.isChecked():
                bmr = ceil(655.1 + (9.563 * float(weight)) + (1.85 * float(height)) - (4.676 * float(age)))
            else:
                bmr = ceil(66.5 + (13.75 * float(weight)) + (5.003 * float(height)) - (6.755 * float(age)))

            self.bmr_result_lbl.setText(str(bmr))

            exersize = self.exersize_combo.currentText()

            if exersize == "1-3 Hours":
                exersize_multpilier = 1.20
            elif exersize == "4-6 Hours":
                exersize_multpilier = 1.35
            elif exersize == "6+ Hours":
                exersize_multpilier = 1.50

            tdee = ceil(bmr * exersize_multpilier)

            self.tdee_result_lbl.setText(str(tdee))

            if self.cut_radio.isChecked():
                aim = -500
            elif self.maintain_radio.isChecked():
                aim = 0
            else:
                aim = 500

            daily_calories = tdee + aim

            self.calorie_result.setText(str(daily_calories))
        except ValueError:
            pass

    def km(self):
        self.age_entry.setDisabled(True)
        self.height_entry.setDisabled(True)
        self.body_fat_entry.setDisabled(False)

    def hb(self):
        self.age_entry.setDisabled(False)
        self.height_entry.setDisabled(False)
        self.body_fat_entry.setDisabled(True)

    def calculate_bmr(self):
        pass

    def shopping_list_tab(self):
        if self.tabs.currentIndex() == 6:
            global product_list
            product_list = []
            self.shopping_list_table.setRowCount(0)
            self.shopping_list_table_non_tesco.setRowCount(0)
            self.shopping_list_calculate([self.groupBox_11, self.groupBox_12])

    def shopping_list_calculate(self, areas):
        conn = sqlite3.connect("food.db")
        product_list = []
        for area in areas:
            widgets = area.children()
            for widget in widgets:
                if isinstance(widget, QtWidgets.QTableWidget):
                    rows = widget.rowCount()
                    if rows > 0:
                        row = 0
                        for each in range(rows):

                            if widget.item(row, 1).text() == "Recipe":

                                cursor_object = conn.cursor()

                                cursor_object.execute("SELECT rowid, * FROM meals_table WHERE meal_name = ?",
                                                      (widget.item(row, 2).text(),))

                                portion = widget.item(row, 11).text()
                                ingredients = cursor_object.fetchall()[0]
                                servings = ingredients[11]
                                ingredients_list = ingredients[9].split(", ")
                                portion_list = ingredients[10].split(", ")
                                portion_list_index = 0
                                for ingredient in ingredients_list:
                                    cursor_object.execute("SELECT rowid, * FROM food_table WHERE rowid = ?",
                                                          (ingredient,))

                                    ingredient_list = list(cursor_object.fetchall()[0])
                                    ingredient_list.insert(13, ingredient_list[11])
                                    ingredient_list.insert(14, ingredient_list[12])

                                    # Calculates portion required based on number of servings in recipe multiplied by number
                                    # of portions on meal planner
                                    ingredient_list[11] = (float(portion_list[portion_list_index]) / float(servings)) * float(portion)
                                    # Calculates calories per portion of ingredient
                                    ingredient_list[12] = int((float(ingredient_list[14]) / float(ingredient_list[13])) * float(
                                        ingredient_list[11]))

                                    portion_list_index += 1

                                    table = self.is_tesco(ingredient_list[4])

                                    self.add_product_to_shopping_list(table, ingredient_list, product_list)
                                    product_list.append(int(ingredient_list[0]))

                            else:
                                table = self.is_tesco(widget.item(row, 4).text())
                                ingredient_list = []
                                col = 0
                                while col < 18:
                                    item = widget.item(row, col).text()
                                    ingredient_list.append(item)

                                    col += 1

                                self.add_product_to_shopping_list(table, ingredient_list, product_list)
                                product_list.append(int(ingredient_list[0]))

                            row += 1
        conn.close()

    def is_tesco(self, id):
        if id == "":
            table = self.shopping_list_table_non_tesco
        else:
            table = self.shopping_list_table
        return table

    def add_product_to_shopping_list(self, table, item_list, product_list):
        if int(item_list[0]) in product_list:
            row = 0
            for each in range(table.rowCount()):
                if int(table.item(row, 0).text()) == int(item_list[0]):
                    quantity = float(table.item(row, 11).text()) + float(item_list[11])
                    table.setItem(row, 11, QtWidgets.QTableWidgetItem(str(quantity)))
                row += 1
        else:
            row = table.rowCount()
            table.insertRow(row)
            col = 0
            for each in item_list:
                table.setItem(row, col, QtWidgets.QTableWidgetItem(str(each)))
                col += 1
        self.shopping_list_quantity(table)


    def shopping_list_quantity(self, table):
        full_row_count = table.rowCount()
        full_rows = 0
        while full_rows < full_row_count:

            quantity = ceil(float(table.item(full_rows, 11).text()) / float(
                table.item(full_rows, 17).text()))
            if quantity == 0:
                quantity = 1
            table.setItem(full_rows, 18, QtWidgets.QTableWidgetItem(str(quantity)))

            category = table.item(full_rows, 1).text()
            category_number = dictionary_food[category]
            table.setItem(full_rows, 19, QtWidgets.QTableWidgetItem(str(category_number)))


            full_rows += 1
        table.setSortingEnabled(True)
        table.sortItems(19, QtCore.Qt.AscendingOrder)
        shopping_list_table_height = (full_row_count * 40) + 50
        if shopping_list_table_height > 800:
            shopping_list_table_height = 800
        table.setFixedHeight(shopping_list_table_height)

    def new(self):
        self.clear_week("phil")
        self.clear_week("vikki")

    def file_open(self, startup=False):
        if startup:
            file_name = ["Startup.txt"]
        else:
            file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Open", "", "Text Files (*.txt)")
        file = open(file_name[0], "r")
        if file.mode == "r":
            contents = file.read()
            contents_list = contents.split("new_line")
            for entry in contents_list:
                entry_list = entry.split(",")
                table_name_pop = entry_list.pop(0).replace("[", "")
                table_name = table_name_pop.replace("'", "")
                if "phil" in table_name:
                    area = self.groupBox_11
                else:
                    area = self.groupBox_12
                table = area.findChild(QtWidgets.QTableWidget, table_name)
                if table != None:
                    row_position = table.rowCount()
                else:
                    break
                table.insertRow(row_position)
                col = 0
                for each in entry_list:
                    data = each.replace("]", "").strip()[1:-1]
                    table.setItem(row_position, col, QtWidgets.QTableWidgetItem(str(data)))
                    if col != 11:
                        new_item = table.item(row_position, col)
                        new_item.setFlags(QtCore.Qt.ItemIsEditable)
                    col += 1

        self.meal_planner_calculate()
        file.close()

    def file_save_as(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(None, "Save As", "", "Text Files (*.txt)")
        file = open(file_name[0],"w+")
        if file_name != "":
            food = self.save()
        file.write(food)
        file.close()

        global file_name_store
        file_name_store = file_name[0]

    def file_save(self):
        if file_name_store == "":
            self.file_save_as()
        else:
            file = open(file_name_store, "w")
            food = self.save()
            file.write(food)

    def save(self):
        foods = ""
        for widget in self.groupBox_11.children():
            if isinstance(widget, QtWidgets.QTableWidget):
                rows = widget.rowCount()
                row = 0
                for each in range(rows):
                    if rows > 0:
                        col = 0
                        food = [widget.objectName()]
                        while col < 18:
                            item = widget.item(row, col).text()
                            food.append(item)
                            col += 1
                        row += 1

                        foods += str(food)
                        foods += "new_line"

        for widget in self.groupBox_12.children():
            if isinstance(widget, QtWidgets.QTableWidget):
                rows = widget.rowCount()
                row = 0
                for each in range(rows):
                    if rows > 0:
                        col = 0
                        food = [widget.objectName()]
                        while col < 18:
                            item = widget.item(row, col).text()
                            food.append(item)
                            col += 1
                        row += 1

                        foods += str(food)
                        foods += "new_line"

        return foods

    def exit(self):
        reply = QtWidgets.QMessageBox.question(None, "Exit?", "Do you really want to quit?")
        if reply == QtWidgets.QMessageBox.Yes:
            QtCore.QCoreApplication.quit()



    def get_tesco_data(self):
        url = self.add_food_url_search_entry.text()
        if url != "":
            try:
                browser = webdriver.Chrome(
                        executable_path="chromedriver.exe")
                browser.get(url)

                pack_size = browser.find_element_by_id("net-contents")
                pack_size1 = pack_size.find_element_by_css_selector("p")
                try:
                    if "kilograms" in pack_size1.text.lower():
                        pack_size2 = re.sub('[kilograms℮]', '', pack_size1.text.lower())
                        pack_size_g = float(pack_size2) * 1000
                    elif "grams" in pack_size1.text.lower() and "x" in pack_size1.text.lower():
                        pack_size2 = pack_size1.text.lower()
                        pack_size3 = pack_size2.split("x")
                        pack_size4 = pack_size3[0]
                        pack_size5 = pack_size4.strip()
                    elif "grams" in pack_size1.text.lower():
                        pack_size2 = re.sub('[grams℮]', "", pack_size1.text.lower())
                    elif "biscuits" in pack_size1.text.lower() and "x" in pack_size1.text.lower():
                        pack_size2 = pack_size1.text.lower()
                        pack_size3 = pack_size2.split("x")
                        pack_size4 = pack_size3[0]
                        pack_size5 = pack_size4.strip()
                except:
                    pass

                product_name = browser.find_element_by_class_name("product-details-tile__title")
                result_product_name = product_name.text
                self.add_food_name_entry.clear()
                self.add_food_name_entry.setText(result_product_name)

                headers_table = browser.find_elements_by_class_name("product__info-table/*")
                for header_table in headers_table:
                    header = header_table.find_elements_by_xpath("./thead/tr/th")

                for index1, headers in enumerate(header):
                    if headers.text == "Typical Values":
                        calories_per = re.sub('[^0-9.]', '', header[index1 + 1].text)
                        self.add_food_per_g_entry.clear()
                        self.add_food_per_g_entry.setText(calories_per)

                count = 0
                web_macros_table = browser.find_elements_by_class_name("product__info-table/*")
                for web_macro_table in web_macros_table:
                    web_macros = web_macro_table.find_elements_by_xpath("./tbody/tr/td")
                    for index, web_macro in enumerate(web_macros):

                        if "Fat" in web_macro.text:
                            result_fat = re.sub('[^0-9.]', '', web_macros[index + 1].text)
                            self.add_food_fat_entry.clear()
                            self.add_food_fat_entry.setText(result_fat)

                        if "Carbohydrate" in web_macro.text:
                            result_carbs = re.sub('[^0-9.]', '', web_macros[index + 1].text)
                            self.add_food_carbs_entry.clear()
                            self.add_food_carbs_entry.setText(result_carbs)

                        if "sugar" in web_macro.text.lower():
                            result_sugar = re.sub('[^0-9.]', '', web_macros[index + 1].text)
                            self.add_food_sugar_entry.clear()
                            self.add_food_sugar_entry.setText(result_sugar)

                        if "Protein" in web_macro.text:
                            result_protein = re.sub('[^0-9.]', '', web_macros[index + 1].text)
                            self.add_food_protein_entry.clear()
                            self.add_food_protein_entry.setText(result_protein)

                        if "kcal" in web_macro.text.lower() and "kj" in web_macro.text.lower():
                            while count == 0:
                                kcal = web_macro.text.lower()
                                count += 1
                                kcal_list = kcal.split("/")
                                # kcal_list = kcal.split(" ")
                                result_energy = re.sub('[^0-9.]', '', kcal_list[1])
                                port_size_get = web_macros[index + 1].text
                                if any(char.isdigit() for char in port_size_get):
                                    # port_size_split = port_size_get.split("/ ")
                                    port_size_split1 = re.split(" |/", port_size_get)
                                    port_size_split = []
                                    for split in port_size_split1:
                                        if split != "":
                                            port_size_split.append(split)
                                    port_size_calc = re.sub('[^0-9.]', '', port_size_split[1])
                                    port_size = round(int(port_size_calc) / int(result_energy) * 100)
                                    cal_per_portion = round(port_size * (int(result_energy) / int(calories_per)))
                                else:
                                    port_size = 1
                                    cal_per_portion = round(port_size * (int(result_energy) / int(calories_per)))



                        elif "kcal" in web_macro.text.lower():
                            while count == 0:
                                if not any(char.isdigit() for char in web_macro.text.lower()):
                                    kcal = web_macros[index + 1].text
                                else:
                                    kcal = web_macro.text

                                count += 1
                                result_energy = re.sub('[^0-9]', '', kcal)

                                if "%" in web_macros[index + 1].text:
                                    a = web_macros[index + 1].text.split("(")
                                    port_size = re.sub('[^0-9.]', '', a[0])
                                    port_size_check = round(((float(port_size) / int(result_energy)) * 100), 1)
                                    if str(port_size_check) in pack_size1.text:
                                        cal_per_portion = port_size
                                        port_size = "1"

                                else:
                                    port_size = re.sub('[^0-9.]', '', web_macros[index + 1].text)
                                    port_size_res = int(port_size) / int(result_energy)

                                    port_size = round(port_size_res * 100)
                                    cal_per_portion = port_size * (int(result_energy) / int(calories_per))
                                    cal_per_portion = round(cal_per_portion)

                self.add_food_calories_entry.clear()
                self.add_food_calories_entry.setText(result_energy)

                self.add_food_portion_size_entry.clear()
                self.add_food_portion_size_entry.setText(str(port_size))

                self.add_food_calories_per_portion_entry.clear()
                self.add_food_calories_per_portion_entry.setText(str(cal_per_portion))

                browser.quit()

            except:
                browser.quit()
                self.message_box("Error", "Unable To Retrieve Data")


    def add_new_food(self):
        url = self.add_food_url_search_entry.text()
        product_id = url.split("/")
        cat_var_read = self.add_food_category_combo.currentText()
        name_text_read = self.add_food_name_entry.text()
        cal_text_read = self.add_food_calories_entry.text()
        perg_text_read = self.add_food_per_g_entry.text()
        fat_text_read = self.add_food_fat_entry.text()
        pro_text_read = self.add_food_protein_entry.text()
        carb_text_read = self.add_food_carbs_entry.text()
        sug_text_read = self.add_food_sugar_entry.text()
        port_size_read = self.add_food_portion_size_entry.text()
        cal_per_portion_read = self.add_food_calories_per_portion_entry.text()
        pack_size_read = self.add_food_pack_size_entry.text()

        if name_text_read != "" and cal_text_read != "" and perg_text_read != "" and fat_text_read != "" and pro_text_read != "" and carb_text_read != "" and sug_text_read != "" and port_size_read != "" and cal_per_portion_read != "" and pack_size_read != "":

            try:
                new_food = [cat_var_read,
                            name_text_read,
                            url,
                            product_id[-1],
                            cal_text_read,
                            perg_text_read,
                            fat_text_read,
                            pro_text_read,
                            carb_text_read,
                            sug_text_read,
                            port_size_read,
                            cal_per_portion_read,
                            "",
                            "",
                            pack_size_read]

                conn = sqlite3.connect("food.db")
                cursorObject = conn.cursor()

                if product_id[-1] == '':
                    data = (new_food)
                    cursorObject.execute("INSERT INTO food_table VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (data))
                    self.message_box("Added", "Item Added")
                    self.clear_entry()
                else:
                    cursorObject.execute("SELECT rowid, * FROM food_table WHERE Tesco_id = ?", (product_id[-1],))
                    row_id = cursorObject.fetchall()
                    if not row_id:
                        data = (new_food)
                        cursorObject.execute("INSERT INTO food_table VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (data))
                        self.message_box("Added", "Item Added")
                        self.clear_entry()
                    else:
                        row_id_tuple = row_id[0]
                        if product_id[-1] == str(row_id_tuple[4]):
                            self.message_box("Error", "Item already exists in database")

                conn.commit()
                conn.close()
            except:
                self.message_box("Error", "Error, Item Not Added")
        else:
            self.message_box("Error", "Please complete all fields")

    def clear_entry(self):
        self.add_food_url_search_entry.clear()
        self.add_food_name_entry.clear()
        self.add_food_calories_entry.clear()
        self.add_food_per_g_entry.clear()
        self.add_food_fat_entry.clear()
        self.add_food_protein_entry.clear()
        self.add_food_carbs_entry.clear()
        self.add_food_sugar_entry.clear()
        self.add_food_portion_size_entry.clear()
        self.add_food_calories_per_portion_entry.clear()

    def message_box(self, title, message):
        self.app = QtWidgets.QMessageBox()
        self.app.setWindowTitle(title)
        self.app.setText(message)
        self.app.exec()

    def search_edit_food(self):
        self.edit_food_table.setRowCount(0)
        search_name = self.edit_food_url_search_entry.text()
        search_type = self.edit_food_category_combo.currentText()

        conn = sqlite3.connect("food.db")
        cursor_object = conn.cursor()

        if search_type == "All":
            cursor_object.execute("SELECT rowid, * FROM food_table WHERE Type != ? AND name LIKE ?",
                                  ("Recipe", "%" + search_name + "%",))
        else:
            cursor_object.execute("SELECT rowid, * FROM food_table WHERE name LIKE ? AND Type = ?",
                                  ("%" + search_name + "%", search_type))

        for each in cursor_object.fetchall():
            if search_type == "Deleted" and each[1] == "Deleted":
                row_position = self.edit_food_table.rowCount()
                self.edit_food_table.insertRow(row_position)
                col = 0
                for row in each:
                    self.combo = QtWidgets.QComboBox()
                    self.combo.addItems(categories_food_del)
                    if col == 1:
                        self.edit_food_table.setCellWidget(row_position, 1, self.combo)
                        self.combo.setCurrentText(row)
                    else:
                        self.edit_food_table.setItem(row_position, col, QtWidgets.QTableWidgetItem(str(row)))

                    col += 1

            elif search_type != "Deleted" and each[1] != "Deleted":
                row_position = self.edit_food_table.rowCount()
                self.edit_food_table.insertRow(row_position)
                col = 0
                for row in each:
                    self.combo = QtWidgets.QComboBox()
                    self.combo.addItems(categories_food)

                    if col == 1:
                        self.edit_food_table.setCellWidget(row_position, 1, self.combo)
                        self.combo.setCurrentText(row)
                    else:
                        self.edit_food_table.setItem(row_position, col, QtWidgets.QTableWidgetItem(str(row)))

                    col += 1

        conn.close()

    def edit_food_save(self):
        conn = sqlite3.connect("food.db")
        cursor_object = conn.cursor()
        row = 0
        row_count = self.edit_food_table.rowCount()
        while row <= (row_count - 1):
            row_edit_list = []
            row_id = self.edit_food_table.item(row, 0).text()
            col = 0
            while col <= 15:
                if col == 1:
                    widget = self.edit_food_table.cellWidget(row, col)
                    row_edit = widget.currentText()
                else:
                    row_edit = self.edit_food_table.item(row, col).text()
                    (row_edit)
                row_edit_list.append(row_edit)
                col += 1

            cursor_object.execute(
                "UPDATE food_table SET Type = (?), name = (?), URL = (?), Tesco_id = (?), Calories = (?), Per_G = (?), Fat = (?), Protein = (?), Carbohydrate = (?), Sugar = (?), Portion_size = (?), Calories_per_portion = (?), Recipe_num = (?), recipes_in = (?), Pack_size = (?) WHERE _rowid_ = (?)",
                (row_edit_list[1], row_edit_list[2], row_edit_list[3], row_edit_list[4], row_edit_list[5], row_edit_list[6],
                 row_edit_list[7], row_edit_list[8], row_edit_list[9], row_edit_list[10], row_edit_list[11],
                 row_edit_list[12], row_edit_list[13], row_edit_list[14], row_edit_list[15], row_id))
            conn.commit()

            row += 1

        conn.close()

    def edit_food_delete(self):
        current_row = self.edit_food_table.currentRow()
        try:
            row_id = self.edit_food_table.item(current_row, 0).text()
            name = self.edit_food_table.item(current_row, 2).text()

            conn = sqlite3.connect("food.db")
            cursor_object = conn.cursor()

            cursor_object.execute("SELECT rowid, meal_name, ingredients FROM meals_table")
            data = cursor_object.fetchall()
            name_present_list = []
            for data_list in data:

                name_list = [data_list[1]]
                recipe_string = data_list[2]

                recipe_list = recipe_string.split(",")

                for each in recipe_list:
                    recipe_num = each.strip()
                    name_list.append(recipe_num)
                if row_id in name_list:
                    name_present_list.append(name_list[0])

            if name_present_list:
                name_present_string = ", ".join(name_present_list)
                app = QtWidgets.QMessageBox()
                app.setWindowTitle("Warning")
                app.Icon(QtWidgets.QMessageBox.Question)
                app.setText("Ingredient exists in:" + name_present_string + ". \n\nAre you sure you want to delete?")
                app.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                app.setDefaultButton(QtWidgets.QMessageBox.No)
                reply = app.exec()
                if reply == QtWidgets.QMessageBox.Yes:
                    cursor_object.execute(
                        "UPDATE food_table SET Type = (?) WHERE _rowid_ = (?)",
                        ("Deleted", row_id))
                    conn.commit()
                    deleted = QtWidgets.QMessageBox()
                    deleted.setWindowTitle("Success")
                    deleted.setText(name + " Deleted")
                    deleted.exec()
                    self.search_edit_food()
            else:
                cursor_object.execute(
                    "UPDATE food_table SET Type = (?) WHERE _rowid_ = (?)",
                    ("Deleted", row_id))
                conn.commit()
                deleted1 = QtWidgets.QMessageBox()
                deleted1.setWindowTitle("Success")
                deleted1.setText(name + " Deleted")
                deleted1.exec()
                self.search_edit_food()

        except AttributeError:
            self.message_box("Error", "Please Select Item To Delete")

    def search_food_meal(self, search_bar, table, combo):
        table.setRowCount(0)
        search_name = search_bar.text()
        search_type = combo.currentText()
        min_calories = 0
        max_calories = 10000
        if table.objectName() == "meal_planner_search_table":
            min_calories = self.min_cal_entry.text()
            max_calories = self.max_cal_entry.text()


        try:
            conn = sqlite3.connect("food.db")
        except:
            self.message_box("Error", "Can't access database")
        cursor_object = conn.cursor()

        if search_name == "" and search_type == "All":
            cursor_object.execute("SELECT rowid, * FROM food_table WHERE Type != ? AND Calories_per_portion <= ?" 
                            "AND Calories_per_portion >= ? ORDER BY RANDOM() Limit 30", ("Recipe", max_calories, min_calories))

        elif search_name == "":
            cursor_object.execute("SELECT rowid, * FROM food_table WHERE Type = ? AND Calories_per_portion <= ?"
                                  "AND Calories_per_portion >= ? ORDER BY RANDOM() Limit 30",
                                  (search_type, max_calories, min_calories))

        elif search_type == "All":
            cursor_object.execute("SELECT rowid, * FROM food_table WHERE Type != ? AND name LIKE ? AND Calories_per_portion <= ?"
                                  "AND Calories_per_portion >= ?", ("Recipe", "%" + search_name + "%", max_calories, min_calories))
        else:
            cursor_object.execute("SELECT rowid, * FROM food_table WHERE name LIKE ? AND Type = ? "
                                  "AND Calories_per_portion <= ? AND Calories_per_portion >= ?",
                                  ("%" + search_name + "%", search_type, max_calories, min_calories))

        for each in cursor_object.fetchall():
            if each[1] != "Deleted":
                row_position = table.rowCount()
                table.insertRow(row_position)
                col = 0
                for row in each:
                    table.setItem(row_position, col, QtWidgets.QTableWidgetItem(str(row)))
                    col += 1
        conn.close()

    def add_ingredient(self, table1, table2, calc, carb_entry, pro_entry, fat_entry, sugar_entry, cal_entry, serv):
        #try:
        row_position = table1.rowCount()
        table1.insertRow(row_position)
        row = table2.currentRow()
        col = 0
        while col < 17:
            if col >= 13:
                table1.setItem(row_position, col, QtWidgets.QTableWidgetItem(table2.item(row, col - 2)))
                new_item = table1.item(row_position, col)
                new_item.setFlags(QtCore.Qt.ItemIsEditable)
            else:
                if col != 11:
                    table1.setItem(row_position, col, QtWidgets.QTableWidgetItem(table2.item(row, col)))
                    new_item = table1.item(row_position, col)
                    new_item.setFlags(QtCore.Qt.ItemIsEditable)
                else:
                    table1.setItem(row_position, col, QtWidgets.QTableWidgetItem(table2.item(row, col)))
            col += 1

        calc(table1, carb_entry, pro_entry, fat_entry, sugar_entry, cal_entry, serv)

        #except AttributeError:
            #table1.removeRow(table1.rowCount() - 1)
            #self.message_box("Error", "Please Select Item To Add")

    def add_meal_calculate(self, table, carb_entry, pro_entry, fat_entry, sugar_entry, cal_entry, serv):
        total_carbs = 0.0
        total_protein = 0.0
        total_fat = 0.0
        total_sugar = 0.0
        total_calories = 0.0
        servings = serv.text()
        if servings == "":
            servings = 1.0
        row = 0
        row_count = table.rowCount()
        if row_count == 0:
            carb_entry.clear()
            pro_entry.clear()
            fat_entry.clear()
            cal_entry.clear()
            sugar_entry.clear()
        try:
            while row <= (row_count - 1):
                per_g = table.item(row, 6).text()
                cal_per_g = table.item(row, 5).text()
                total_cal = table.item(row, 14).text()
                portion_in_grams = float(per_g) / float(cal_per_g) * float(total_cal)
                multiplier = float(table.item(row, 11).text()) / float(table.item(row, 13).text())

                carbs = table.item(row, 9).text()
                carbs_float = ((float(carbs) / float(per_g)) * float(portion_in_grams)) / float(servings) * float(multiplier)
                total_carbs += carbs_float
                total_carbs = round(total_carbs, 2)
                carb_entry.clear()
                carb_entry.setText(str(total_carbs))

                protein = table.item(row, 8).text()
                protein_float = ((float(protein) / float(per_g)) * float(portion_in_grams)) / float(servings) * float(
                    multiplier)
                total_protein += protein_float
                total_protein = round(total_protein, 2)
                pro_entry.clear()
                pro_entry.setText(str(total_protein))

                fat = table.item(row, 7).text()
                fat_float = ((float(fat) / float(per_g)) * float(portion_in_grams)) / float(servings) * float(multiplier)
                total_fat += fat_float
                total_fat = round(total_fat, 2)
                fat_entry.clear()
                fat_entry.setText(str(total_fat))

                sugar = table.item(row, 10).text()
                sugar_float = ((float(sugar) / float(per_g)) * float(portion_in_grams)) / float(servings) * float(multiplier)
                total_sugar += sugar_float
                total_sugar = round(total_sugar, 2)
                sugar_entry.clear()
                sugar_entry.setText(str(total_sugar))

                calories = table.item(row, 12).text()
                calories_float = float(calories) / float(servings)
                total_calories += calories_float
                total_calories = round(total_calories, 2)
                cal_entry.clear()
                cal_entry.setText(str(int(total_calories)))
                cal_entry.setText(str(int(total_calories)))

                row += 1
        except ValueError:
            self.message_box("Error", "Select row to add!")
            table.removeRow(table.rowCount()-1)

    def meal_delete_ingredient(self, table, calc, carb_entry, pro_entry, fat_entry, sugar_entry, cal_entry, serving_entry):
        row = table.currentRow()
        table.removeRow(row)

        calc(table, carb_entry, pro_entry, fat_entry, sugar_entry, cal_entry, serving_entry)

    def change_meal_portion(self, table, row, col):
        if col == 11:
            calories = float(table.item(row, 14).text()) / float(
                table.item(row, 13).text()) * float(table.item(row, 11).text())
            current_calories = float(table.item(row, 12).text())
            if int(current_calories) != int(calories):
                table.setItem(row, 12, QtWidgets.QTableWidgetItem(str(int(calories))))
                new_item = table.item(row, 12)
                new_item.setFlags(QtCore.Qt.ItemIsEditable)
                new_item.setFlags(QtCore.Qt.ItemIsSelectable)

                if table == self.add_meal_recipe_table:
                    self.add_meal_calculate(self.add_meal_recipe_table, self.add_meal_carbs_entry,
                                            self.add_meal_protein_entry, self.add_meal_fat_entry,
                                            self.add_meal_sugar_entry, self.add_meal_calories_entry,
                                            self.add_meal_servings_entry)
                else:
                    self.add_meal_calculate(self.edit_meal_recipe_table, self.edit_meal_carbs_entry,
                                            self.edit_meal_protein_entry, self.edit_meal_fat_entry,
                                            self.edit_meal_sugar_entry, self.edit_meal_calories_entry,
                                            self.edit_meal_servings_entry)

    def add_meal_todb(self, table, name, recipe_book, page, carbs, protein, fat, sugar, calories, servings):
        meal_name = name.text()
        recipe_book = recipe_book.text()
        page_no = page.text()
        carbs = carbs.text()
        protein = protein.text()
        fat = fat.text()
        sugar = sugar.text()
        calories = calories.text()
        servings = servings.text()
        ingredients = []
        portions = []
        row = 0
        row_count = table.rowCount()
        while row <= (row_count - 1):
            ingredient = table.item(row, 0).text()
            ingredients.append(ingredient)
            ingredient_str = ', '.join(ingredients)

            portion = table.item(row, 11).text()
            portions.append(portion)
            portion_str = ', '.join(portions)

            row += 1

        try:
            meal = [meal_name, recipe_book, page_no, carbs, protein, fat, sugar, calories, ingredient_str, portion_str, servings]

            conn = sqlite3.connect("food.db")
            cursor_object = conn.cursor()

            data1 = (meal)

            global meal_id
            if meal_id == None:
                data2 = [""]
                data = data1 + data2
                cursor_object.execute("INSERT INTO meals_table VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (data))

                a = cursor_object.execute('SELECT max(rowid) FROM meals_table')
                meal_id = a.fetchone()
                meal_id_str = re.sub('[,()]', '', str(meal_id))

                food = ["Recipe", meal_name, "", "", calories, 1, fat, protein, carbs, sugar, "1", calories, meal_id_str,
                        "", "1"]

                cursor_object.execute("INSERT INTO food_table VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (food))
                food_row_id = cursor_object.execute('SELECT max(rowid) FROM food_table')
                food_row_id_get = food_row_id.fetchone()
                food_row_id_str = re.sub('[,()]', '', str(food_row_id_get))

                cursor_object.execute("UPDATE meals_table SET food_table_number = (?) WHERE _rowid_ = (?)", (food_row_id_str, meal_id_str))

            else:
                cursor_object.execute("UPDATE meals_table SET meal_name = (?), recipe_book = (?), page = (?), carbs = (?), protein = (?), fat = (?), sugar = (?), calories = (?), ingredients = (?), portions  = (?), servings = (?) WHERE _rowid_ = (?)",
                                      (meal_name, recipe_book, page_no, carbs, protein, fat, sugar, calories, ingredient_str, portion_str, servings, meal_id))
                meal_id_str = str(meal_id)
                food_row_id = cursor_object.execute('SELECT food_table_number FROM meals_table WHERE _rowid_ = (?)', (meal_id_str))
                food_row_id_get = food_row_id.fetchone()
                food_row_id_str = re.sub('[,()]', '', str(food_row_id_get))
                cursor_object.execute("UPDATE food_table SET type = (?), name = (?), Calories = (?), Fat = (?), Protein = (?), Carbohydrate = (?), Sugar = (?), Calories_per_portion = (?) WHERE _rowid_ = (?)",
                                      ("Recipe", meal_name, calories, fat, protein, carbs, sugar, calories, food_row_id_str))

            for ingredient_number in ingredients:
                meals_in = cursor_object.execute('SELECT recipes_in FROM food_table WHERE rowid = ?', (ingredient_number,))
                meals_in_get = meals_in.fetchone()
                if not meals_in_get[0]:
                    meals_in_write = str(meal_id_str)
                    cursor_object.execute("UPDATE food_table SET recipes_in = ? WHERE rowid = ?",
                                          (str(meals_in_write), ingredient_number,))
                else:
                    meals = str(meals_in_get)
                    meals1 = re.sub("['()]", '', str(meals))
                    meals2 = meals1[:-1]
                    meals_list1 = meals2.split(",")
                    meals_list2 = []
                    for z in meals_list1:
                        meals_list2.append(int(z))
                    if int(meal_id_str) not in meals_list2 or not meals_list2:
                        meals_in_write = meals_in_get + (int(meal_id_str),)

            conn.commit()
            conn.close()
        except UnboundLocalError:
            self.message_box("Error", "Meal Not Valid!")

    def search_edit_meal(self):
        self.edit_meal_table.setRowCount(0)
        search_name = self.edit_meal_search_entry.text()

        conn = sqlite3.connect("food.db")
        cursor_object = conn.cursor()

        cursor_object.execute("SELECT rowid, * FROM meals_table WHERE meal_name LIKE ?", ("%" + search_name + "%",))
        for each in cursor_object.fetchall():
            row_position = self.edit_meal_table.rowCount()
            self.edit_meal_table.insertRow(row_position)
            col = 0
            for row in each:
                self.edit_meal_table.setItem(row_position, col, QtWidgets.QTableWidgetItem(str(row)))
                col += 1

        conn.close()


    def edit_meal_choose(self):
        self.edit_meal_recipe_table.setRowCount(0)
        row = self.edit_meal_table.currentRow()
        try:
            row_id = self.edit_meal_table.item(row, 0).text()

            conn = sqlite3.connect("food.db")
            cursor_object = conn.cursor()

            cursor_object.execute("SELECT rowid, * FROM meals_table WHERE rowid = ?", (row_id,))
            a = cursor_object.fetchall()
            b = a[0]
            c = b[9]
            d = str(c).split(",")
            z = str(b[10]).split(",")
            global meal_id
            meal_id = a[0][0]

            self.edit_meal_name_entry.clear()
            self.edit_meal_name_entry.setText(b[1])
            self.edit_meal_recipe_book_entry.clear()
            self.edit_meal_recipe_book_entry.setText(b[2])
            self.edit_meal_page_entry.clear()
            self.edit_meal_page_entry.setText(str(b[3]))
            self.edit_meal_servings_entry.clear()
            self.edit_meal_servings_entry.setText(str(b[11]))

            for index, each in enumerate(d):
                e = each.strip(" ")

                cursor_object.execute("SELECT rowid, * FROM food_table WHERE rowid =?", (e,))
                for f in cursor_object.fetchall():
                    row_position = self.edit_meal_recipe_table.rowCount()
                    self.edit_meal_recipe_table.insertRow(row_position)
                    col = 0
                    for g in f:
                        if col == 11:
                            if float(z[index]) > 1:
                                portion = str(int(float(z[index])))
                            else:
                                portion = str(z[index])
                            self.edit_meal_recipe_table.setItem(row_position, col, QtWidgets.QTableWidgetItem(portion.strip()))
                        elif col == 13 or col == 14:
                            self.edit_meal_recipe_table.setItem(row_position, col, QtWidgets.QTableWidgetItem(str(f[col-2])))
                        else:
                            self.edit_meal_recipe_table.setItem(row_position, col, QtWidgets.QTableWidgetItem(str(g)))
                        calories = float(z[index]) / float(f[11]) * float(f[12])
                        self.edit_meal_recipe_table.setItem(row_position, 12, QtWidgets.QTableWidgetItem(str(ceil(calories))))
                        if col != 11:
                            new_item = self.edit_meal_recipe_table.item(row_position, col)
                            new_item.setFlags(QtCore.Qt.ItemIsEditable)
                        new_item = self.edit_meal_recipe_table.item(row_position, 12)
                        new_item.setFlags(QtCore.Qt.ItemIsEditable)
                        col += 1

            self.add_meal_calculate(self.edit_meal_recipe_table, self.edit_meal_carbs_entry, self.edit_meal_protein_entry, self.edit_meal_fat_entry, self.edit_meal_sugar_entry, self.edit_meal_calories_entry, self.edit_meal_servings_entry)
        except AttributeError:
            self.message_box("Error", "Select row to add!")

    def add_button(self, button_name):
        try:
            if "phil" in button_name.objectName():
                area = self.scrollAreaWidgetContents_4
            else:
                area = self.scrollAreaWidgetContents_7
            table_name = button_name.objectName().replace("add_button", "table")
            table = area.findChild(QtWidgets.QTableWidget, table_name)
            row_position = table.rowCount()
            row = self.meal_planner_search_table.currentRow()
            if row != -1:
                table.insertRow(row_position)
            else:
                return
            col = 0
            while col < 18:
                if col >= 13:
                    table.setItem(row_position, col,
                                  QtWidgets.QTableWidgetItem(self.meal_planner_search_table.item(row, col - 2)))
                else:
                    if col != 11:
                        table.setItem(row_position, col,
                                      QtWidgets.QTableWidgetItem(self.meal_planner_search_table.item(row, col)))
                        new_item = table.item(row_position, col)
                        new_item.setFlags(QtCore.Qt.ItemIsEditable)
                    else:
                        table.setItem(row_position, col,
                                      QtWidgets.QTableWidgetItem(self.meal_planner_search_table.item(row, col)))
                col += 1

            self.meal_planner_calculate()

        except AttributeError:
            self.message_box("Error", "Select row to add!")
            table.removeRow(table.rowCount()-1)


    def delete_button(self, button_name):
        if "phil" in button_name.objectName():
            area = self.scrollAreaWidgetContents_4
        else:
            area = self.scrollAreaWidgetContents_7
        table_name = button_name.objectName().replace("delete_button", "table")
        table = area.findChild(QtWidgets.QTableWidget, table_name)
        row = table.currentRow()
        table.removeRow(row)

        self.meal_planner_calculate()


    def copy_button(self, button_name):
        if "phil" in button_name.objectName():
            area = self.scrollAreaWidgetContents_4
        else:
            area = self.scrollAreaWidgetContents_7
        table_name = button_name.objectName().replace("copy_button", "table")
        table = area.findChild(QtWidgets.QTableWidget, table_name)
        rows = table.rowCount()
        row = 0

        data_string = ""
        while row < rows:
            col = 0
            while col < 18:
                item = table.item(row, col)
                data_string += item.text()
                data_string += ", "
                col += 1
            row += 1
        pyperclip.copy(data_string)

    def paste_button(self, button_name):
        '''
        :param button_name: Takes name of button that is clicked.
        :pastes the copied row ot the table linked to the buttton.
        '''
        data_string = pyperclip.paste()
        item = data_string.split(", ")
        list_list = []
        while len(item) > 1:
            list = []
            for each in range(18):
                pop = item.pop(0)
                list.append(pop)
            list_list.append(list)

        if "phil" in button_name.objectName():
            area = self.scrollAreaWidgetContents_4
        else:
            area = self.scrollAreaWidgetContents_7
        table_name = button_name.objectName().replace("paste_button", "table")
        table = area.findChild(QtWidgets.QTableWidget, table_name)
        row = table.rowCount()
        for each in list_list:
            table.insertRow(row)
            col = 0
            for item in each:
                if col != 11:
                    table.setItem(row, col, QtWidgets.QTableWidgetItem(item))
                    new_item = table.item(row, col)
                    new_item.setFlags(QtCore.Qt.ItemIsEditable)
                else:
                    table.setItem(row, col, QtWidgets.QTableWidgetItem(item))
                col += 1
            row += 1

        self.meal_planner_calculate()


    def copy_day1(self, day, person):
        '''
        :param day: takes day from the button pressed
        :param person: takes person from the button pressed
        :copies day and person to the clipboard.
        '''
        copy = day + "," + person
        pyperclip.copy(copy)


    def paste_day1(self, day, person):
        self.clear_day(person, day)
        copy = pyperclip.paste()
        copy_list = copy.split(",")
        try:
            if "phil" == copy_list[1] or "vikki" == copy_list[1] and copy_list[0] in day_list:
                copy_day = copy_list[0]
                if copy_list[1] == "phil":
                    area = self.groupBox_11
                else:
                    area = self.groupBox_12
                for widget in area.children():
                    if isinstance(widget, QtWidgets.QTableWidget):
                        if copy_day in widget.objectName():
                            rows = widget.rowCount()
                            row = 0
                            if rows > 0:
                                copy_widget = widget.objectName()
                                copy_widget_list = copy_widget.split("_")
                                new_widget = person + "_" + day + "_" + copy_widget_list[2] + "_table"
                                if person == "phil":
                                    paste_widget = self.scrollAreaWidgetContents_4.findChild(QtWidgets.QTableWidget,
                                                                                             new_widget)
                                else:
                                    paste_widget = self.scrollAreaWidgetContents_7.findChild(QtWidgets.QTableWidget,
                                                                                             new_widget)
                                paste_widget.setRowCount(0)
                                while row < rows:
                                    data_string = ""
                                    col = 0
                                    while col < 17:
                                        item = widget.item(row, col)
                                        data_string += item.text() + ", "
                                        col += 1
                                    row += 1
                                    data_list = data_string.split(",")
                                    paste_row = paste_widget.rowCount()
                                    paste_widget.insertRow(paste_row)
                                    col1 = 0
                                    for each in data_list:
                                        if col1 != 11:
                                            paste_widget.setItem(paste_row, col1, QtWidgets.QTableWidgetItem(each))
                                            new_item = paste_widget.item(paste_row, col1)
                                            new_item.setFlags(QtCore.Qt.ItemIsEditable)
                                        else:
                                            paste_widget.setItem(paste_row, col1, QtWidgets.QTableWidgetItem(each))
                                        col1 += 1
        except IndexError:
            pass

        self.meal_planner_calculate()


    def copy_week(self, old_person, new_person):
        if old_person == "phil":
            area = self.groupBox_11
            new_area = self.groupBox_12
        else:
            area = self.groupBox_12
            new_area = self.groupBox_11

        for widget in area.children():
            if isinstance(widget, QtWidgets.QTableWidget):
                rows = widget.rowCount()
                row = 0
                if rows > 0:
                    copy_widget = widget.objectName()
                    copy_widget_list = copy_widget.split("_")
                    new_widget = new_person + "_" + copy_widget_list[1] + "_" + copy_widget_list[2] + "_table"
                    paste_widget = new_area.findChild(QtWidgets.QTableWidget, new_widget)
                    paste_widget.setRowCount(0)
                    while row < rows:
                        paste_widget.insertRow(paste_widget.rowCount())
                        #paste_widget.setRowHeight(row, 5)
                        col = 0
                        while col < 18:
                            item = widget.item(row, col).text()
                            if col != 11:
                                paste_widget.setItem(row, col, QtWidgets.QTableWidgetItem(item))
                                new_item = paste_widget.item(row, col)
                                new_item.setFlags(QtCore.Qt.ItemIsEditable)
                            else:
                                paste_widget.setItem(row, col, QtWidgets.QTableWidgetItem(item))
                            col += 1
                        row += 1

        self.meal_planner_calculate()


    def clear_week(self, person):
        if person == "phil":
            area = self.groupBox_11
        else:
            area = self.groupBox_12
        for widget in area.children():
            if isinstance(widget, QtWidgets.QTableWidget):
                widget.setRowCount(0)

        self.meal_planner_calculate()


    def clear_day(self, person, day):
        if person == "phil":
            area = self.groupBox_11
        else:
            area = self.groupBox_12
        for widget in area.children():
            if isinstance(widget, QtWidgets.QTableWidget) and (person and day) in widget.objectName():
                widget.setRowCount(0)

        self.meal_planner_calculate()


    def change_planner_portion(self, table, row, col):
        if col == 11:
            calories = float(table.item(row, 14).text()) / float(table.item(row, 13).text()) * float(
                table.item(row, 11).text())
            current_calories = float(table.item(row, 12).text())
            if int(current_calories) != int(calories):
                table.setItem(row, 12, QtWidgets.QTableWidgetItem(str(int(calories))))
                new_item = table.item(row, 12)
                new_item.setFlags(QtCore.Qt.ItemIsEditable)

                self.meal_planner_calculate()

    def meal_planner_calculate(self):
        people = ["phil", "vikki"]
        for person in people:
            if person == "phil":
                area = self.groupBox_11
            else:
                area = self.groupBox_12
            for day in day_list:
                total_carbs = 0.0
                total_protein = 0.0
                total_fat = 0.0
                total_sugar = 0.0
                total_calories = 0.0
                for widget in area.children():
                    if isinstance(widget, QtWidgets.QTableWidget) and day in widget.objectName():
                        row = 0
                        while widget.rowCount() > row:
                            if widget.columnCount() >= 11:
                                calories = float(widget.item(row, 14).text()) / float(widget.item(row, 13).text()) * \
                                           float(widget.item(row, 11).text())
                                current_calories = float(widget.item(row, 12).text())
                                if current_calories != calories:
                                    widget.setItem(row, 12, QtWidgets.QTableWidgetItem(str(int(calories))))
                                    new_item = widget.item(row, 12)
                                    new_item.setFlags(QtCore.Qt.ItemIsEditable)

                                per_g = widget.item(row, 6).text()
                                cal_per_g = widget.item(row, 5).text()
                                total_cal = widget.item(row, 14).text()
                                portion_in_grams = float(per_g) / float(cal_per_g) * float(total_cal)
                                multiplier = float(widget.item(row, 11).text()) / float(widget.item(row, 13).text())

                                carbs = ((float(widget.item(row, 9).text()) / float(per_g)) * float(
                                    portion_in_grams)) * float(multiplier)
                                protein = ((float(widget.item(row, 8).text()) / float(per_g)) * float(
                                    portion_in_grams)) * float(multiplier)
                                fat = ((float(widget.item(row, 7).text()) / float(per_g)) * float(
                                    portion_in_grams)) * float(multiplier)
                                sugar = ((float(widget.item(row, 10).text()) / float(per_g)) * float(
                                    portion_in_grams)) * float(multiplier)
                                row += 1
                                total_carbs += carbs
                                total_protein += protein
                                total_fat += fat
                                total_sugar += sugar
                                total_calories += calories
                carbs_widget = area.findChild(QtWidgets.QLineEdit, f"{person}_{day}_carbs_entry")
                carbs_widget.clear()
                carbs_widget.setText(str(round(total_carbs, 2)))
                protein_widget = area.findChild(QtWidgets.QLineEdit, f"{person}_{day}_protein_entry")
                protein_widget.clear()
                protein_widget.setText(str(round(total_protein, 2)))
                fat_widget = area.findChild(QtWidgets.QLineEdit, f"{person}_{day}_fat_entry")
                fat_widget.clear()
                fat_widget.setText(str(round(total_fat, 2)))
                sugar_widget = area.findChild(QtWidgets.QLineEdit, f"{person}_{day}_sugar_entry")
                sugar_widget.clear()
                sugar_widget.setText(str(round(total_sugar, 2)))
                calories_widget = area.findChild(QtWidgets.QLineEdit, f"{person}_{day}_calories_entry")
                calories_widget.clear()
                calories_widget.setText(str(round(total_calories, 2)))

app = QtWidgets.QApplication([])
app.setStyle('Fusion')
window = MainWindow()
window.show()
window.file_open(startup=True)
window.add_food_url_search_entry.setText("https://www.tesco.com/groceries/en-GB/products/268767943")

sys.exit(app.exec_())

