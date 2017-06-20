import sys
import json
from pprint import pprint

# the backup data in json format.
data = dict()

# flag[card_hash] = whether the card is flagged or not.
flag = dict()

# rev_g[card_hash] = list of accounts linked to it.
rev_g = dict()

# own_card[card_hash] = whether this card is part of the chain (ucard not a card) or not.
own_card = dict()

# g[account_hash] = list of cards linked to it.
g = dict()


# get_chain(account_hash, card_hash) = the longest chain that we can pass through starting from this account and card.
def get_chain(cur_account, cur_card):
	# if cur_card has more than two accounts linked to it then it is not a ucard.
	if len(rev_g[cur_card]) != 2:
		# return a chain of length 1 containing the current account and current card.
		return ([cur_account], [cur_card])

	# get the other account linked to cur_card.
	new_account = rev_g[cur_card][0]
	if new_account == cur_account:
		new_account = rev_g[cur_card][1]

	# initialize the result with a chain of length 1.
	result = ([cur_account], [cur_card])

	# iterate over all cards linked to the new_account.
	for i in range(len(g[new_account])):
		# get the new card.
		new_card = g[new_account][i]

		# check if the new card is not the same as cur_card to avoid cycles.
		if new_card != cur_card:
			# get the longest possible chain from going through the new_account and new_card.
			sub_result = get_chain(new_account, new_card)
			sub_result = ([cur_account] + sub_result[0], [cur_card] + sub_result[1])

			# check if that chain is longer than the current result then update the result.
			if len(sub_result[0]) > len(result[0]):
				result = sub_result

	return result

# read the json from a file given as a command line parameter.
with open(sys.argv[1]) as data_file:
	data = json.load(data_file)

# iterate over the data to fill in flag, g and rev_g.
for account in data:
	# get the hash of the account of this data item.
	account_hsh = account['account']
	# iterate over all the cards in the current data item.
	for card in account['cards']:
		# get the hash of the card.
		card_hsh = card['card']

		# if the card_hash is not in rev_g then initialize it. 
		if not (card_hsh in rev_g):
			rev_g[card_hsh] = []

		# add the account to the list of accounts linked to card_hsh
		rev_g[card_hsh] += [account_hsh]

		# if the account_hsh is not in g then initialize it.
		if not (account_hsh in g):
			g[account_hsh] = []

		# add the card to the list of cards linked to account_hsh
		g[account_hsh] += [card_hsh]

		# check if a flagged attribute exists in the card's item then mark this card as flagged.
		if 'flagged' in card:
			flag[card_hsh] = 1

# search for a possible uaccount0x1
for account_hsh in g.keys():
	# check if the account has only 2 cards linked to it.
	if len(g[account_hsh]) == 2:
		# get the longest chain using the first card linked to the account.
		sub_result_1 = get_chain(account_hsh, g[account_hsh][0])

		# get the longest chain using the second card linked to the account.
		sub_result_2 = get_chain(account_hsh, g[account_hsh][1])

		# get the longest chain from both found chains.
		result = sub_result_1
		if len(sub_result_2[0]) > len(result[0]):
			result = sub_result_2

		# if the length of the chain is at least 64 then it is our chain.
		if len(result[0]) >= 64:
			# iterate over all the cards in the chain and mark them as ucards.
			for card in range(len(result[1])):
				own_card[result[1][card]] = 1

			output = ""
			# iterate over the 64 uaccounts to get the flags of the ccards.
			for i in range(64):
				# get the hash of the account.
				account = result[0][i]

				# since ucards are all not flagged,
				# then if any card linked to this uaccount is flagged, it must be the ccard.
				inflag = False
				for i in range(len(g[account])):
					if g[account][i] in flag:
						inflag = True
						
				if inflag:
					output += "1"
				else:
					output += "0"
			print(output)
