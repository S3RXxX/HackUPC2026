import subprocess
import tempfile
import json
from typing import List, Dict, Any
import subprocess
import os
import requests
import csv
from pathlib import Path




def load_llm_instructions(instructions_path: str = "llm_instructions.txt") -> str:
    """Load the LLM prompt instructions from a text file"""

    with open(instructions_path, 'r', encoding='utf-8') as f:
        instructions = f.read()
    print(f"Loaded LLM instructions from {instructions_path}")
    return instructions

def analyze_code(code: str) -> List[Dict[str, Any]]:
    results = []

    results.extend(run_ruff(code))

    return results


# ----------------------------
# Ruff analyzer
# ----------------------------

def run_ruff(code: str) -> List[Dict[str, Any]]:
    issues = []

    with tempfile.NamedTemporaryFile(suffix=".py", delete=True, mode="w") as f:
        f.write(code)
        f.flush()

        try:
            result = subprocess.run(
                ["ruff", "check", f.name, "--output-format", "json"],
                capture_output=True,
                text=True
            )

            if result.stdout:
                data = json.loads(result.stdout)

                for item in data:
                    issues.append({
                        "tool": "ruff",
                        "type": item.get("type", "warning"),
                        "message": item.get("message", ""),
                        "line": item.get("location", {}).get("row"),
                        "rule": item.get("code")
                    })

        except Exception as e:
            issues.append({
                "tool": "ruff",
                "type": "error",
                "message": str(e)
            })

    return issues


class DeepSeekDetector:
    def __init__(self, csv_path: str = "antipatterns.csv", instructions_path: str = "llm_instructions.txt"):
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.malpractices = self.load_malpractice_db(csv_path)
        self.instructions_path = instructions_path
    
    def load_malpractice_db(self, csv_path: str) -> List[Dict]:
        malpractices = []
        
        if not Path(csv_path).exists():
            print(f"❌ Malpractice database not found at {csv_path}")
            return []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    malpractices.append({
                        'name': row.get('name', ''),
                        'category': row.get('category', ''),
                        'description': row.get('description', ''),
                        'bad_example': row.get('bad_example', ''),
                        'good_example': row.get('good_example', ''),
                        'suggestion': row.get('suggestion', '')
                    })
            print(f" Loaded {len(malpractices)} malpractices from {csv_path}")
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return []
        
        return malpractices
    
    def load_instructions(self) -> str:
        """Load LLM instructions from file"""
        try:
            with open(self.instructions_path, 'r', encoding='utf-8') as f:
                instructions = f.read()
            print(f"Loaded instructions from {self.instructions_path}")
            return instructions
        except FileNotFoundError:
            print(f"Instructions file not found at {self.instructions_path}")
            raise
        except Exception as e:
            print(f"Error loading instructions: {e}")
            raise
    
    def format_malpractices_for_prompt(self) -> str:
        if not self.malpractices:
            return "No malpractices in database"
        
        formatted = []
        for mp in self.malpractices[:20]:
            formatted.append(f"- {mp['name']} ({mp['category']}): {mp['description']}")
            if mp.get('suggestion'):
                formatted.append(f"  Fix: {mp['suggestion']}")
        
        return '\n'.join(formatted)
    
    def detect_with_llm(self, code: str) -> List[Dict[str, Any]]:
        """Use DeepSeek LLM to detect malpractices using instructions from file"""
        
        if not self.api_key:
            print("DeepSeek API key not set. Skipping LLM detection.")
            print("   Set DEEPSEEK_API_KEY environment variable to enable")
            return []
        
        if not self.malpractices:
            print("No malpractices loaded from CSV. Skipping LLM detection.")
            return []
        
        try:
            # Load instructions from file
            instructions_template = self.load_instructions()
            
            # Format malpractice database
            malpractices_text = self.format_malpractices_for_prompt()
            
            # Build the prompt using the instructions template
            prompt = instructions_template.format(
                malpractices_text=malpractices_text,
                code=code[:3000]
            )
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a Python code quality expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                llm_output = result['choices'][0]['message']['content']
                
                try:
                    # Clean up the response
                    llm_output = llm_output.strip()
                    if llm_output.startswith('```json'):
                        llm_output = llm_output[7:]
                    if llm_output.startswith('```'):
                        llm_output = llm_output[3:]
                    if llm_output.endswith('```'):
                        llm_output = llm_output[:-3]
                    
                    findings = json.loads(llm_output)
                    
                    # Format issues with all the requested fields
                    issues = []
                    for finding in findings:
                        issues.append({
                            "tool": "deepseek-llm",
                            "type": "malpractice",
                            "malpractice_name": finding.get('malpractice', 'Unknown'),
                            "line": finding.get('line'),
                            "explanation": finding.get('explanation', ''),
                            "message": f"[{finding.get('malpractice', 'Unknown')}] {finding.get('explanation', '')}",
                            "rule": finding.get('malpractice', ''),
                            "suggestion": finding.get('suggestion', '')
                        })
                    return issues
                    
                except json.JSONDecodeError as e:
                    print(f"Failed to parse LLM response as JSON: {e}")
                    print(f"Raw response: {llm_output[:200]}...")
                    return []
            else:
                print(f"DeepSeek API error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return []
                
        except FileNotFoundError as e:
            print(f"Instructions file not found: {e}")
            return []
        except KeyError as e:
            print(f"Instructions template missing placeholder: {e}")
            print("   Make sure {malpractices_text} and {code} are in the template")
            return []
        except Exception as e:
            print(f"LLM detection failed: {e}")
            return []


def print_results(results: List[Dict[str, Any]]) -> None:
    if not results:
        print("\n No issues detected.")
        return

    print("\nAnalysis Results:\n")

    for i, issue in enumerate(results, 1):
        print(f"[{i}] Tool: {issue.get('tool')}")
        print(f"    Type: {issue.get('type')}")
        print(f"    Message: {issue.get('message')}")
        print(f"    Rule: {issue.get('rule', 'N/A')}")
        print(f"    Line: {issue.get('line', 'N/A')}")
        print("-" * 50)


if __name__ == "__main__":
    sample_code = """ 

from Pizza import Pizza

class Cashier:
    def __init__(self, chef):
        self.chef = chef
        self.frequent_customer_discount = False
        self.first_name = None
        self.last_name = None
        self.address = None
        self.phone_number = None
        self.email = None
        self.temp_discount_code = None
        self.temp_order_note = None

    def take_order(self, pizza_type: str):
        print(f"Cashier is taking order for {pizza_type} pizza.")
        self.chef.bake_pizza(pizza_type)

    def hurry_up_chef(self):
        print("Cashier is hurrying up the chef.")
        self.chef.hurry_up()

    def calm_customer_down(self):
        print("Cashier is calming the customer down.")
        self.chef.clean_kitchen()

    def deliver_pizza_to_customer(self):
        print("Cashier is delivering pizza to the customer.")

    def ask_for_receipt(self):
        print("Customer is asking for a receipt.")

    def another_unused_method(self):
        pass

    def yet_another_unused_method(self):
        pass

    def long_method(self):
        print("Cashier is handling many tasks in a single method")
        self.take_order("Cheese")
        self.hurry_up_chef()
        self.calm_customer_down()
        self.deliver_pizza_to_customer()
        self.ask_for_receipt()

    def order_with_unnecessary_details(self, pizza_type, size, crust_type, toppings, extra_cheese, discount_code):
        print(f"Placing a detailed order for {pizza_type} pizza with {size}, {crust_type}, {toppings}, extra cheese: {extra_cheese}, discount code: {discount_code}")
        self.take_order(pizza_type)
        self.apply_discount(discount_code)
        self.deliver_pizza_to_customer()

    def duplicate_method(self):
        print("Customer is making a duplicate order")
        self.take_order("Cheese")
        self.take_order("Cheese")

    def chain_of_methods(self):
        print("Cashier is initiating a message chain")
        self.chef.clean_kitchen()

    def middleman_method(self):
        print("Cashier is calling a middleman method")
        self.middle_method()

    def middle_method(self):
        print("Middleman method delegating to another method")
        self.real_method()

    def real_method(self):
        print("Real method doing the actual work")

    def access_internal_details(self):
        print(f"Accessing internal details: {self.chef.busy}")

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

    def apply_discount(self, discount_code):
        print(f"Applying discount for customer with code {discount_code}")

    def apply_loyalty_points(self):
        print("Applying loyalty points for customer")

    def handle_complaint(self, complaint):
        if complaint == "cold pizza":
            self.calm_customer_down()
        elif complaint == "late delivery":
            self.calm_customer_down()
        elif complaint == "wrong order":
            self.calm_customer_down()
        else:
            self.calm_customer_down()

    def refused_bequest(self):
        pass"""

    results = analyze_code(sample_code)
    print_results(results)