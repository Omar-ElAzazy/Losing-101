# [Anonymous exchange](https://capturetheflag.withgoogle.com/challenges/)

#### Getting to know the challenge

>I've bought some bitcoins with my credit cards, and some of them attracted attention, but I don't know which ones. Could you find out?

>Challenge running at anon.ctfcompetition.com:1337

I tried connecting to it using netcat and received

```sh
Hey. Could you tell me if my cards ccard0x1 through ccard0x40 have attracted the wrong type of attention? Flagged cards are displayed in their dumps, and their encryption is deterministic. I seem to have the wrong encoding on my terminal, so I'll need help there.
I'll patch you into a management interface in a few seconds.


Welcome to our telnet dogecoin exchange !.
We've currently frozen most of the operations pending an investigation into potential credit card fraud with law enforcement.
 - NEWACC to create an account.
 - NEWCARD to create a test credit card.
 - ASSOC <cardx> <accounty> to associate cardx to accounty.
 - BACKUP to generate a anonymized encrypted jsonified maybe-emojified backup.
```
I tried using the commands to see how it works.

```sh
NEWACC
OK: Account uaccount0x1 created.
```
```sh
NEWCARD
OK: Card ucard0x1 created.
```
```sh
ASSOC ucard0x1 uaccount0x1
OK: Card ucard0x1 associated with account uaccount0x1.
```
```sh
ASSOC ccard0x1 uaccount0x1
OK: Card ccard0x1 associated with account uaccount0x1.
```
```sh
BACKUP
[{"account":"8c0b47580572db7b","cards":[{"card":"2f5f9d384de92ef8"},{"card":"068dc3795f105fed","flagged":"1"},{"card":"c1f65b722cff1649"}]},
...
{"account":"8b6cf1d560ea3e23","cards":[{"card":"2f5f9d384de92ef8"},{"card":"65a2e03f256a5be0"},{"card":"4392c0cda8095143"}]}]


So, which cards are burnt?
Answer with a string of zeroes and ones, no spaces.
test
Wait, that's not right. I expected 1001111011100110010110110010011110001011001101101101000101011110...
```

So, I can create new cards, new accounts, link cards to accounts and at the end get an encrypted backup of the whole network (Including more data than I created) and try to guess which from the ccards are flagged.

After some trials I figured out that we can link at most 3 cards to a single account. 

I thought about spamming the network with accounts, link ccard0x1 with 300 accounts, link ccard0x2 with 601 accounts and so on. This way the card linked to between 300 and 600 accounts is ccard0x1, the card linked to between 601 and 900 accounts is ccard0x2 and so on. This way I identified the ccards in the network and I can check whether it is flagged or not.

```sh
NEWACC
OK: Account uaccount0x1 created.
ASSOC ccard0x1 uaccount0x1
OK: Card ccard0x1 associated with account uaccount0x1.
NEWACC
OK: Account uaccount0x2 created.
ASSOC ccard0x1 uaccount0x2
OK: Card ccard0x1 associated with account uaccount0x2.
NEWACC
OK: Account uaccount0x3 created.
ASSOC ccard0x1 uaccount0x3
OK: Card ccard0x1 associated with account uaccount0x3.
NEWACC
OK: Account uaccount0x4 created.
ASSOC ccard0x1 uaccount0x4
KO: Too many accounts already use this card.
```

It turns out we can't link more than 3 account to a single card as well ...

#### The challenge

* There is a network of ccards and caccounts with some associations between them.
* Some of the ccards are flagged.
* I can create uaccounts and they will be added to the network.
* I can create ucards and they will be added to the network.
* I can associate ucards/ccards to uaccounts.
* I can associate at most 3 cards to an account.
* I can associate at most 3 accounts to a card.
* I can get a backup for the network, but all the card and account names will be encrypted.
* In the backup I can't identify cards and accounts.
* I need to get which ccards are flagged.

I will be using the term "extra data", I mean by that the caccounts and the associations between caccounts and ccards.

#### The solution

I thought that to solve it, we need to link each ccard to a unique uaccount and to be able to identify the uaccounts.

So I started with creating 64 uaccounts and linking them to the ccards as shown in the figure below.

<p align="center">
  <img src="https://github.com/Omar-ElAzazy/Losing-101/raw/master/ctfs/2017-06-18-Google-CTF/Anonymous-exchange/graph1.png" />
</p>

Now I have to be able to identify the uaccounts in the backup. To do that, I created 64 ucards and linked each uaccount0xi and uaccount0x(i+1) to ucard0xi forming the graph below.

<p align="center">
  <img src="https://github.com/Omar-ElAzazy/Losing-101/raw/master/ctfs/2017-06-18-Google-CTF/Anonymous-exchange/graph2.png" />
</p>

The uaccounts and ucards subgraph is similar to a linked list (i.e. forming a chain) and it is probably longer than any other chain appearing in the extra data. So, all we had to do is search for that longest chain (i.e. uaccount0x1 -> ucard0x1 -> uaccount0x2 -> ucard0x2 -> ... -> uaccount0x40 -> ucard0x40). 
Once we have the chain we can easily get the flags of ccard0x1 to ccard0x40.

To get uaccount0x1, it is simply the only uaccount in the chain that is linked to only 2 cards. 

To get ccard0x1, it is the card linked to uaccount0x1 that is not inside the chain. Then we start iterating over the accounts in the chain getting the flags of all the ccards.

I used a bash script to generate the commands to the server.

```bash
echo -e NEWACC"\\n"NEWCARD"\\n"ASSOC ucard0x1 uaccount0x1"\\n"ASSOC ccard0x1 uaccount0x1 &&
for i in `seq 2 64`; do echo -e NEWACC"\\n"NEWCARD"\\n"ASSOC ucard0x$(printf '%x' `expr $i - 1`) uaccount0x$(printf '%x' $i)"\\n"ASSOC ucard0x$(printf '%x' $i) uaccount0x$(printf '%x' $i)"\\n"ASSOC ccard0x$(printf '%x' $i) uaccount0x$(printf '%x' $i); done
```
And used a python script to parse the backup and generate the output. You can find the script [here](https://github.com/Omar-ElAzazy/Losing-101/blob/master/ctfs/2017-06-18-Google-CTF/Anonymous-exchange/search.py).


#### Why does it work?

The uaccounts and ucards chain alternates between uaccounts and ucards. The chain's length is equal to the number of accounts + the number of cards which is 128 in this case.

Since there are only 64 ccards in the extra data, this chain is probably longer than any chain appearing in the extra data. But it is still possible to have a similar chain in the extra data. In case we want to avoid this case, we can create uaccount0x41, ucard0x41 and ucard0x42 then link uaccount0x41 to ucard0x40, ucard0x41 and ucard0x42 so the length of the chain becomes 130. Since there are only 64 cards in the extra data, the length of the longest chain appearing in the extra data is 128. Thus, the artificial chain we created in the network becomes definitely longer than any possible chain in the extra data.

In the CTF, I didn't need to do it since the probability of having such long chain in the extra data is really low.

I also didn't need to worry about complexity since the search space was small.
