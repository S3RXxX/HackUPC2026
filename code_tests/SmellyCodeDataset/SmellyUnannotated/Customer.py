"""
Copyright (c) 2025 Ahmed R. Sadik, Honda Research Institute Europe GmbH 

This source code is licensed under the MIT License found in the
LICENSE file in the root directory of this source tree. This dataset contains smelly code for research and refactoring purposes.
"""


from Drink import Drink

class Customer:
    def __init__(self, pizza_shop):
        self.pizza_shop = pizza_shop
        self.frequent_customer_discount = False
        self.first_name = None
        self.last_name = None
        self.address = None
        self.phone_number = None
        self.email = None
        self.temp_discount_code = None
        self.temp_order_note = None
        self.drink_order = Drink()

    def order_pizza(self, pizza_type: str):
        print(f"Customer is placing an order for {pizza_type} pizza.")
        self.pizza_shop.receive_order(pizza_type)

    def complain(self, complaint: str):
        print(f"Customer is complaining: {complaint}")
        self.pizza_shop.casher.calm_customer_down()
        self.pizza_shop.casher.chef.clean_kitchen()

    def ask_for_receipt(self):
        print("Customer is asking for a receipt.")

    def another_unused_method(self):
        pass

    def yet_another_unused_method(self):
        pass

    def long_complaint_method(self):
        print("Customer is complaining about many things")
        self.complain("Pizza is cold")
        self.complain("Pizza is late")
        self.complain("Wrong pizza delivered")
        self.complain("Pizza is burnt")
        self.complain("Too little cheese")
        self.complain("Pizza is undercooked")
        self.ask_for_receipt()

    def order_with_unnecessary_details(self):
        print("Customer is placing a detailed order")
        self.order_pizza("Veggie", "Large", "Whole Wheat", "Veggies", False, True, False, False, "Olives", "Mushrooms", "Pesto", "Thick", False, False, True, True, True, False, False, False)

    def duplicate_complaint(self):
        print("Customer is complaining about duplicate issues")
        self.complain("Pizza is cold")
        self.complain("Pizza is cold")
        self.complain("Pizza is late")
        self.complain("Pizza is late")

    def chain_of_methods(self):
        print("Customer is initiating a message chain")
        self.pizza_shop.casher.chef.clean_kitchen()

    def middleman_method(self):
        print("Customer is calling a middleman method")
        self.middle_method()

    def middle_method(self):
        print("Middleman method delegating to another method")
        self.real_method()

    def real_method(self):
        print("Real method doing the actual work")

    def access_internal_details(self):
        print(f"Accessing internal details of PizzaShop: {self.pizza_shop.casher.chef.busy}")

    def update_contact_info(self, first_name, last_name, address, phone_number, email):
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.phone_number = phone_number
        self.email = email

    def update_name(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def update_address(self, address):
        self.address = address

    def update_phone_number(self, phone_number):
        self.phone_number = phone_number

    def update_email(self, email):
        self.email = email

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
            self.complain("Pizza is cold")
        elif complaint == "late delivery":
            self.complain("Pizza is late")
        elif complaint == "wrong order":
            self.complain("Wrong pizza delivered")
        else:
            self.complain("General complaint")

    def refused_bequest(self):
        pass

    def order_drink(self, drink_type: str):
        print(f"Customer is ordering a {drink_type} drink.")
        self.drink_order.create_order(drink_type)
        print("Adding the drink order to the current order.")
        self.drink_order.add_to_order()
        print("Confirming the drink order.")
        self.drink_order.confirm_order()
