# from pathlib import Path
import os
from django.shortcuts import render,redirect
from django.core.management.utils import get_random_secret_key

import time
import json
from web3 import Web3
from solcx import compile_standard, install_solc
from .models import transactions

install_solc("0.8.0")

module_dir = os.path.dirname(__file__)  # get current directory
file_path = os.path.join(module_dir, 'Main.sol')

with open(file_path, "r") as file:
    Main_contract = file.read()

#to save the output in a JSON file
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Main.sol": {"content": Main_contract}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] # output needed to interact with and deploy contract 
                }
            }
        },
    },
    solc_version="0.8.0",
)
print(compiled_sol)
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)
    
    
bytecode = compiled_sol["contracts"]["Main.sol"]["Main"]["evm"]["bytecode"]["object"]
# get abi
abi = json.loads(compiled_sol["contracts"]["Main.sol"]["Main"]["metadata"])["output"]["abi"]


w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
chain_id = 1337
address = "0x8906573010E6eD14faac8aBd6ce7B1A96aA54529"
private_key = "0xafa25fba4612488ec2bfc7ed00da3ccd1dd8f511d6a01203588307e9eccbd9a7" # leaving the private key like this is very insecure if you are working on real world project
# Create the contract in Python
Main = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the number of latest transaction
nonce = w3.eth.getTransactionCount(address)

transac = Main.constructor(2,address).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": address,
        "nonce": nonce,
    }
)
# Sign the transaction
sign_transaction = w3.eth.account.sign_transaction(transac, private_key=private_key)
print("Deploying Contract!")
# Send the transaction
transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
# Wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
print(f"Done! Contract deployed to {transaction_receipt.contractAddress}")

Main_list = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)


def transaction(request):
    if request.method=='POST':
        vote=request.POST['vote']
        current_user_address=request.user.first_name
        secret_key=get_random_secret_key()
        temp=str(hash(vote+"#"+current_user_address+"#"+secret_key))
        new_transaction=transactions.objects.create(Vote=temp,secret_key=secret_key,address=current_user_address)
        
        option=Main_list.functions.vote(temp).buildTransaction({"chainId": chain_id, "from": address, "gasPrice": w3.eth.gas_price, "nonce": nonce + 1})
        
        # Sign the transaction
        sign_option = w3.eth.account.sign_transaction(
            option, private_key=private_key
        )
        # Send the transaction
        send_option = w3.eth.send_raw_transaction(sign_option.rawTransaction)
        try:
            transaction_receipt = w3.eth.wait_for_transaction_receipt(send_option)
        except:
            print("transaction failed")
        
        new_transaction.save()
        return redirect('/')
    else:
        return render(request,'transactions.html')

