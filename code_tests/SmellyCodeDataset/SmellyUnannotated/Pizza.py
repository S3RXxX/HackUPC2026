"""
Copyright (c) 2025 Ahmed R. Sadik, Honda Research Institute Europe GmbH 

This source code is licensed under the MIT License found in the
LICENSE file in the root directory of this source tree. This dataset contains smelly code for research and refactoring purposes.
"""


class Pizza:
    def __init__(self, size: str, dough_type: str, topping: str):
        self.size = size
        self.dough_type = dough_type
        self.topping = topping
        self.extra_cheese = False
        self.customer_first_name = None
        self.customer_last_name = None
        self.customer_address = None
        self.customer_phone_number = None
        self.customer_email = None
        self.temp_discount_code = None
        self.temp_order_note = None

    def set_size(self, size: str):
        self.size = size

    def set_dough_type(self, dough_type: str):
        self.dough_type = dough_type

    def set_topping(self, topping: str):
        self.topping = topping

    def update_customer_info(self, first_name, last_name, address, phone_number, email):
        self.customer_first_name = first_name
        self.customer_last_name = last_name
        self.customer_address = address
        self.customer_phone_number = phone_number
        self.customer_email = email

    def update_customer_name(self, first_name, last_name):
        self.customer_first_name = first_name
        self.customer_last_name = last_name

    def update_customer_address(self, address):
        self.customer_address = address

    def update_customer_phone_number(self, phone_number):
        self.customer_phone_number = phone_number

    def update_customer_email(self, email):
        self.customer_email = email

    def notify_for_promotion(self):
        print("Notifying customer for promotion")

    def notify_for_discount(self):
        print("Notifying customer for discount")

    def notify_for_new_arrivals(self):
        print("Notifying customer for new arrivals")

    def apply_discount(self):
        print("Applying discount for customer")

    def apply_loyalty_points(self):
        print("Applying loyalty points for customer")

    def handle_complaint(self, complaint):
        if complaint == "cold pizza":
            print("Handling complaint: Pizza is cold")
        elif complaint == "late delivery":
            print("Handling complaint: Pizza is late")
        elif complaint == "wrong order":
            print("Handling complaint: Wrong pizza delivered")
        else:
            print("Handling complaint: General complaint")

    def ask_for_receipt(self):
        print("Customer is asking for a receipt.")

    def another_unused_method(self):
        pass

    def yet_another_unused_method(self):
        pass

    def long_method(self):
        print("Pizza is handling many tasks in a single method")
        self.set_size("Large")
        self.set_dough_type("Thin Crust")
        self.set_topping("Pepperoni")
        self.update_customer_info("John", "Doe", "123 Street", "555-5555", "john.doe@example.com")
        self.notify_for_promotion()
        self.notify_for_discount()
        self.notify_for_new_arrivals()
        self.apply_discount()
        self.apply_loyalty_points()
        self.handle_complaint("cold pizza")

    def order_with_unnecessary_details(self, pizza_type, size, crust_type, toppings, extra_cheese, discount_code):
        print(f"Placing a detailed order for {pizza_type} pizza with {size}, {crust_type}, {toppings}, extra cheese: {extra_cheese}, discount code: {discount_code}")
        self.set_size(size)
        self.set_dough_type(crust_type)
        self.set_topping(toppings)
        self.apply_discount()

    def duplicate_method(self):
        print("Customer is making a duplicate order")
        self.set_topping("Cheese")
        self.set_topping("Cheese")

    def chain_of_methods(self):
        print("Pizza is initiating a message chain")
        self.update_customer_address("123 Street")

    def middleman_method(self):
        print("Pizza is calling a middleman method")
        self.middle_method()

    def middle_method(self):
        print("Middleman method delegating to another method")
        self.real_method()

    def real_method(self):
        print("Real method doing the actual work")

    def access_internal_details(self):
        print(f"Accessing internal details: {self.size}, {self.dough_type}, {self.topping}")

    def refused_bequest(self):
        pass


class CheesePizza(Pizza):
    def __init__(self):
        super().__init__("Medium", "Regular", "Cheese")
        self.cheese_type = "Mozzarella"

    def handle_complaint(self, complaint):
        if complaint == "too much cheese":
            print("Handling complaint: Too much cheese")
        else:
            super().handle_complaint(complaint)


class VeggiePizza(Pizza):
    def __init__(self):
        super().__init__("Medium", "Whole Wheat", "Veggies")


class TunaPizza(Pizza):
    def __init__(self):
        super().__init__("Large", "Thin Crust", "Tuna")


class PepperoniPizza(Pizza):
    def __init__(self):
        super().__init__("Large", "Regular", "Pepperoni")
