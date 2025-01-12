# SPDX-License-Identifier: MPL-2.0

import sqlite3
import markovify
import time

def make_sentence(cfg):
	class nlt_fixed(markovify.NewlineText):  # modified version of NewlineText that never rejects sentences
		def test_sentence_input(self, sentence):
			return True  # all sentences are valid <3

	cutoff_date = str(time.mktime(time.strptime(cfg["cutoff_date"], '%Y-%m-%d %H:%M:%S')))

	db = sqlite3.connect(cfg["db_path"])
	db.text_factory = str
	c = db.cursor()
	if cfg['learn_from_cw']:
		ignored_cws_query_params = "(" + ",".join("?" * len(cfg["ignored_cws"])) + ")"

		toots = c.execute(
			f"""
			SELECT content
			FROM posts
			WHERE
				(summary IS NULL OR summary NOT IN {ignored_cws_query_params})
				AND published_at > ?
			ORDER BY RANDOM() LIMIT 10000
			""",
			(*cfg["ignored_cws"], cutoff_date,),
		).fetchall()
	else:
		toots = c.execute(
			"""
			SELECT content
			FROM posts
			WHERE summary IS NULL AND published_at > ?
			ORDER BY RANDOM()
			LIMIT 10000
			""",
			(cutoff_date,),
		).fetchall()

	if not toots:
		raise ValueError("Database is empty! Try running main.py.")

	nlt = markovify.NewlineText if cfg['overlap_ratio_enabled'] else nlt_fixed

	# TODO support replicating \n in output posts instead of squashing them together
	model = nlt("\n".join(toot[0].replace('\n', ' ') for toot in toots))

	db.close()

	if cfg['limit_length']:
		sentence_len = randint(cfg['length_lower_limit'], cfg['length_upper_limit'])

	sentence = None
	tries = 0
	for tries in range(10):
		if (sentence := model.make_short_sentence(
			max_chars=500,
			tries=10000,
			max_overlap_ratio=cfg['overlap_ratio'] if cfg['overlap_ratio_enabled'] else 0.7,
			max_words=sentence_len if cfg['limit_length'] else None
		)) is not None:
			break
	else:
		raise ValueError("Failed 10 times to produce a sentence!")

	return sentence
