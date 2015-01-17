lrhiero
========

This is a left-to-right decoder for hierarchical phrase-based (hiero) SMT system.


# Usage
```
python decoder_cp.py --config <lrhiero.ini> --inputfile <test.in> --outputfile <test.out> --ttable-file <test.rule>
```

# Requirements
* Python 2.6 or higher

# Advance Features of the Decoder

## Grammar
LR-Hiero uses a spesific form of SCFG (Synchronous Context-Free Grammar) rules which are prefix-lexicalized or in so-called Greibach Normal Form (GNF) on target side.


### File Format
The content of rule file is for each line: source phrase, target phrase, and features. 
```
aber X__1 sagen X__2 ||| but say X__1 X__2 ||| -0.558224 -0.000100005 -1.14023 -1.84913
```

## Handling Unknown Words
Unknown words are copied verbatim to the output. For each unknown word/phrase 4 glue rules are generated and added to the grammar, therefore they may be placed out of order in the output. Unknown words are also scored by the language model. 

<!--- TODO: add -drop-unknown switch to the decoder
Alternatively, you may want to drop unknown words. To do so add the switch -drop-unknown.

When translating between languages that use different writing sentences (say, Chinese-English), dropping unknown words results in better BLEU scores. However, it is misleading to a human reader, and it is unclear what the effect on human judgment is. 
-->
<!--
## Verbose
Switch -verbose (short -v) displays additional run time information.
-->

# Citation
If you use this decoder in you research, consider citing:
* Efficient Left-to-Right Hierarchical Phrase-based Translation with Improved Reordering. Maryam Siahbani, Baskaran Sankaran and Anoop Sarkar. In Proceedings of the Conference on Empirical Methods in Natural Language Processing (EMNLP 2013). Oct 18-21, 2013. Seattle, USA.


# Contacts
Maryam Siahbani, Anoop Sarkar
{msiahban,anoop}@sfu.ca

NatLang Lab, School of Computing Science
Simon Fraser University, 
Burnaby, BC V5A 1S6. Canada
