## Inspiration
We have seen a ton of security problems that stem from untrusted or insecure compliers. Problems such as XCodeGhost, or just general problems with securely converting code from source to binary has been very difficult in especially in fields that rely on the compiled program to be secure. 

## What it does
DCC solves this problem by distributing the process of compilation. A job is uploaded onto IPFS and sent to a tracker. Clients who wish to earn money by compiling downloads the necessary files from IPFS, compiles it, and uploads the end result back into IPFS.

This process is secured by a smart contract between the sender and worker, and only pays the workers that has produced the right source code (determined by consensus of hash values) the amount. 

## How we built it
We have built it with EVM (Solidity) and Python, where the web server is in flask, and the smart contract is written in Solidity.

## Challenges we ran into
Getting the smart contract to work was a difficult process as we were new to Ethereum and concepts of the EVM, making debugging the code difficult. This is especially challenging since the execution of the EVM code is particularly sensitive to efficiency. 

## Extensibility
We believe that this application can be applied to both the open source community as well as publicly sensitive application such as voting machines. It both ensures the integrity of the binary, and also alleviates the computational stress of the source. 
