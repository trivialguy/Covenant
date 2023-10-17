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
p_address = "0xE4A7c8A616f125D5Cc2f6fDB334D5B89A07DAd57"
private_key = "0x19966923ac2e4649a35a6af2827a58aae93a5ca79f32fcb8cb7b13782e4baf83" # leaving the private key like this is very insecure if you are working on real world project
# Create the contract in Python
Main = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the number of latest transaction
nonce = w3.eth.getTransactionCount(p_address)

transac = Main.constructor(2000000000000000000,p_address).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": p_address,
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
print(f"Transaction mined in block {transaction_receipt['blockNumber']}")
Main_list = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)


#define pk as map of address to private key for testing
pk={"0xE4A7c8A616f125D5Cc2f6fDB334D5B89A07DAd57":"0x19966923ac2e4649a35a6af2827a58aae93a5ca79f32fcb8cb7b13782e4baf83"}
def transaction(request):
    if request.method=='POST':
        vote=request.POST['vote']
        current_user_address=request.user.first_name
        secret_key=get_random_secret_key()
        print(vote)
        temp=str(hash(vote+"#"+current_user_address+"#"+secret_key))
        print(temp)
        new_transaction=transactions.objects.create(Vote=temp,secret_key=secret_key,address=current_user_address)

        txn_hash = Main_list.functions.vote(temp).transact({'from': current_user_address, 'value': w3.toWei(2, 'ether'), 'gas': 200000, 'gasPrice': w3.toWei('50', 'gwei')})
        try:
            receipt = w3.eth.waitForTransactionReceipt(txn_hash, timeout=300)
            print(receipt.status)
        except ValueError as e:
            # Handle the exception here
            print(f"An error occurred: {e}")
            print("transaction failed")
            return redirect('transaction')
        print(f"Transaction mined in block {receipt['blockNumber']}")
        if receipt.status == 1:
            new_transaction.save()
            print("transaction successful")
            length_arr=Main_list.functions.arr_length().call()
            print(length_arr,"lol")
            return redirect('/')
        else:
            print("transaction failed")
            return redirect('transaction')
    else:
        return render(request,'transactions.html')
    
def count(request):
    if request.method=='POST':
        current_user_address=request.user.first_name
        length_arr=Main_list.functions.arr_length().call()
        ind=Main_list.functions.curr_length().call()
        print(ind,length_arr)
        mydata=transactions.objects.all()[ind:length_arr]
        
        for i in range (ind+1,length_arr+1):
            vote_a=hash("A"+"#"+mydata[i-1].address+"#"+mydata[i-1].secret_key)
            vote_b=hash("B"+"#"+mydata[i-1].address+"#"+mydata[i-1].secret_key)
            print(vote_a,vote_b)
            
            function_selector = Main_list.encodeABI(fn_name='countvote', args=[str(vote_a),str(vote_b),i])
            gas_estimate = w3.eth.estimate_gas({'from': current_user_address, 'data': function_selector})
            gas_limit = gas_estimate + 50000
            txn_hash=Main_list.functions.countvote(str(vote_a),str(vote_b),i).transact({'from': current_user_address, 'gas': gas_limit, 'gasPrice': w3.toWei('50', 'gwei')})
            try:
                receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
                if receipt.status==1:
                    print("transaction success")
                else:
                    print("transaction terminated")
            except ValueError as e:
                # Handle the exception here
                print(f"An error occurred: {e}")
                print("transaction failed")
                return redirect('transaction')
        print(ind,length_arr)
        for i in range (ind+1,length_arr+1):
            vote_a=hash("A"+"#"+mydata[i-1].address+"#"+mydata[i-1].secret_key)
            vote_b=hash("B"+"#"+mydata[i-1].address+"#"+mydata[i-1].secret_key)
            print(vote_a,vote_b)
            function_selector = Main_list.encodeABI(fn_name='vote_compare', args=[str(vote_a),str(vote_b),i,mydata[i-1].address])
            gas_estimate = w3.eth.estimate_gas({'from': current_user_address, 'data': function_selector})
            gas_limit = gas_estimate + 50000
            txn_hash=Main_list.functions.vote_compare(str(vote_a),str(vote_b),i,mydata[i-1].address).transact({'from': current_user_address, 'gas': gas_limit, 'gasPrice': w3.toWei('50', 'gwei')})
            
                
            try:
                receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
                # print(receipt)
                if receipt.status==1:
                    print("transaction success")
                else:
                    print("transaction terminated")
            except ValueError as e:
                print(f"An error occurred: {e}")
                print("transaction failed")
                return redirect('transaction')
        return redirect('/')
    else:
        return render(request,'transactions.html')
    

